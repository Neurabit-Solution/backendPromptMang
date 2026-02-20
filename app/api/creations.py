"""
Creations API
-------------
POST /api/creations/generate  → upload image + style_id → Gemini → save to S3 → return result
GET  /api/creations/mine      → current user's creation history
"""

import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.database import get_db
from app.core import security, s3 as s3_service, gemini as gemini_service
from app.models.user import User
from app.models.style import Style, Category
from app.models.style import Creation
from app.schemas.style import GenerateResponse, CreationOut, StyleOut, CategoryOut

router = APIRouter(prefix="/creations", tags=["Creations"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


# ─── Auth helper ─────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = security.verify_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ─── Helper ───────────────────────────────────────────────────────────────────


from app.core.s3 import generate_presigned_url

def _creation_to_out(creation: Creation, credits_remaining: int) -> CreationOut:
    style = creation.style
    cat = style.category
    return CreationOut(
        id=creation.id,
        original_image_url=generate_presigned_url(creation.original_image_url),
        generated_image_url=generate_presigned_url(creation.generated_image_url),
        thumbnail_url=generate_presigned_url(creation.thumbnail_url),
        style=StyleOut(
            id=style.id,
            name=style.name,
            slug=style.slug,
            description=style.description,
            preview_url=generate_presigned_url(style.preview_url),
            category=CategoryOut(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                icon=cat.icon,
                description=cat.description,
                preview_url=generate_presigned_url(cat.preview_url),
                display_order=cat.display_order,
            ),
            uses_count=style.uses_count,
            is_trending=style.is_trending,
            is_new=style.is_new,
            tags=style.tags or [],
            credits_required=style.credits_required,
        ),
        mood=creation.mood,
        weather=creation.weather,
        dress_style=creation.dress_style,
        is_public=creation.is_public,
        credits_used=creation.credits_used,
        credits_remaining=credits_remaining,
        processing_time=creation.processing_time,
        created_at=creation.created_at,
    )


# ─── Generate Endpoint ────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate_image(
    style_id: int = Form(..., description="ID of the style to apply"),
    image: UploadFile = File(..., description="User's photo (JPG/PNG, max 10 MB)"),
    mood: Optional[str] = Form(None),
    weather: Optional[str] = Form(None),
    dress_style: Optional[str] = Form(None),
    custom_prompt: Optional[str] = Form(None, max_length=200),
    is_public: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Main image generation endpoint.

    Flow:
    1. Validate image type & size
    2. Check user has enough credits
    3. Fetch style + its prompt template from DB
    4. Upload original image to S3  (creations/originals/<user_id>/<uuid>.jpg)
    5. Build final prompt  (template + user options)
    6. Call Gemini API with image + prompt
    7. Upload generated image to S3  (creations/generated/<user_id>/<uuid>.jpg)
    8. Save Creation record to DB
    9. Deduct credits from user
    10. Return result
    """

    # ── 1. Validate image ──────────────────────────────────────────────────
    if image.content_type not in ALLOWED_MIME_TYPES:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": {"code": "INVALID_IMAGE", "message": "Only JPG, PNG, and WebP images are supported."}},
        )

    image_bytes = await image.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        return JSONResponse(
            status_code=413,
            content={"success": False, "error": {"code": "IMAGE_TOO_LARGE", "message": "Image must be under 10 MB."}},
        )

    # ── 2. Check credits ───────────────────────────────────────────────────
    style = (
        db.query(Style)
        .options(joinedload(Style.category))
        .filter(Style.id == style_id, Style.is_active == True)
        .first()
    )
    if not style:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"code": "STYLE_NOT_FOUND", "message": "Style not found."}},
        )

    if current_user.credits < style.credits_required:
        return JSONResponse(
            status_code=402,
            content={
                "success": False,
                "error": {
                    "code": "INSUFFICIENT_CREDITS",
                    "message": f"You need {style.credits_required} credits. You have {current_user.credits}.",
                },
            },
        )

    # ── 3. Upload original image to S3 ─────────────────────────────────────
    original_url = s3_service.upload_creation_original(
        file_bytes=image_bytes,
        user_id=current_user.id,
        content_type=image.content_type,
    )

    # ── 4. Build final prompt ──────────────────────────────────────────────
    final_prompt = gemini_service.build_final_prompt(
        prompt_template=style.prompt_template,
        mood=mood,
        weather=weather,
        dress_style=dress_style,
        custom_prompt=custom_prompt,
    )

    # ── 5. Call Gemini ─────────────────────────────────────────────────────
    try:
        generated_bytes, processing_time = gemini_service.transform_image(
            image_bytes=image_bytes,
            image_mime=image.content_type,
            prompt=final_prompt,
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"success": False, "error": {"code": "AI_SERVICE_ERROR", "message": f"AI generation failed: {str(e)}"}},
        )

    # ── 6. Upload generated image to S3 ───────────────────────────────────
    generated_url = s3_service.upload_creation_generated(
        file_bytes=generated_bytes,
        user_id=current_user.id,
        content_type="image/jpeg",
    )

    # ── 7. Save Creation record ────────────────────────────────────────────
    creation = Creation(
        user_id=current_user.id,
        style_id=style.id,
        original_image_url=original_url,
        generated_image_url=generated_url,
        thumbnail_url=generated_url,   # same URL; resize separately if needed
        mood=mood,
        weather=weather,
        dress_style=dress_style,
        custom_prompt=custom_prompt,
        prompt_used=final_prompt,
        credits_used=style.credits_required,
        processing_time=processing_time,
        is_public=is_public,
    )
    db.add(creation)

    # ── 8. Deduct credits & increment style usage ──────────────────────────
    current_user.credits -= style.credits_required
    style.uses_count += 1

    db.commit()
    db.refresh(creation)
    db.refresh(current_user)

    return GenerateResponse(
        success=True,
        data=_creation_to_out(creation, credits_remaining=current_user.credits),
        message="Image generated successfully!",
    )


# ─── My Creations ─────────────────────────────────────────────────────────────

@router.get("/mine")
def my_creations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the current user's creation history (newest first)."""
    creations = (
        db.query(Creation)
        .options(joinedload(Creation.style).joinedload(Style.category))
        .filter(
            Creation.user_id == current_user.id,
            Creation.is_deleted == False,
        )
        .order_by(Creation.created_at.desc())
        .all()
    )

    data = [_creation_to_out(c, credits_remaining=current_user.credits) for c in creations]
    return {"success": True, "data": data, "total": len(data)}
