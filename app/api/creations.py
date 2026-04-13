"""
Creations API
-------------
POST /api/creations/generate      → upload image + style_id → Gemini → save to S3 → return result
GET  /api/creations/mine          → current user's creation history
GET  /api/creations/feed          → community feed (sorted by likes)
POST /api/creations/{id}/like     → like a creation
"""

import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.database import get_db
from app.core import security, s3 as s3_service, gemini as gemini_service
from app.models.user import User
from app.models.style import Style, Category, Creation, CreationLike
from app.schemas.style import GenerateResponse, CreationOut, StyleOut, CategoryOut
from app.core.config import settings
from datetime import datetime, timezone

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


def get_optional_user(
    token: Optional[str] = Depends(security.oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Helper for endpoints that can be public but also respect authentication if provided."""
    if not token:
        return None
    try:
        payload = security.verify_token(token)
        if not payload or payload.get("type") != "access":
            return None
        return db.query(User).filter(User.email == payload.get("sub")).first()
    except Exception:
        return None


# ─── Helper ───────────────────────────────────────────────────────────────────


from app.core.s3 import get_proxy_url

def _creation_to_out(
    creation: Creation,
    credits_remaining: Optional[int] = None,
    is_liked: bool = False
) -> CreationOut:
    style = creation.style
    cat = style.category
    return CreationOut(
        id=creation.id,
        original_image_url=get_proxy_url(creation.original_image_url),
        generated_image_url=get_proxy_url(creation.generated_image_url),
        thumbnail_url=get_proxy_url(creation.thumbnail_url),
        style=StyleOut(
            id=style.id,
            name=style.name,
            slug=style.slug or f"style-{style.id}",
            description=style.description,
            preview_url=get_proxy_url(style.preview_url),
            category=CategoryOut(
                id=cat.id,
                name=cat.name,
                slug=cat.slug or f"category-{cat.id}",
                icon=cat.icon,
                description=cat.description,
                preview_url=get_proxy_url(cat.preview_url),
                display_order=cat.display_order,
            ),
            uses_count=style.uses_count,
            is_trending=style.is_trending,
            is_new=style.is_new,
            tags=style.tags or [],
            credits_required=style.credits_required,
        ),
        user_name=creation.user.name if creation.user else "Anonymous",
        likes_count=creation.likes_count or 0,
        is_liked=is_liked,
        mood=creation.mood,
        weather=creation.weather,
        dress_style=creation.dress_style,
        is_public=creation.is_public,
        credits_used=creation.credits_used,
        credits_remaining=credits_remaining,
        processing_time=creation.processing_time,
        created_at=creation.created_at,
    )


def _refresh_daily_credits(user: User, db: Session) -> User:
    """
    Ensure the user's daily credits are granted for the current day.
    Daily credits are reset every calendar day (UTC) and do not accumulate.
    """
    now = datetime.now(timezone.utc)
    today = now.date()

    if user.daily_credits_date is None or user.daily_credits_date.date() != today:
        user.daily_credits = settings.DAILY_FREE_CREDITS
        user.daily_credits_date = now
        user = db.merge(user)
        db.commit()
        db.refresh(user)

    return user


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
    try:
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

        # Refresh / grant today's daily credits (non-accumulating, expire each day)
        current_user = _refresh_daily_credits(current_user, db)

        total_available_credits = (current_user.credits or 0) + (current_user.daily_credits or 0)
        if total_available_credits < style.credits_required:
            return JSONResponse(
                status_code=402,
                content={
                    "success": False,
                    "error": {
                        "code": "INSUFFICIENT_CREDITS",
                        "message": f"You need {style.credits_required} credits. You have {total_available_credits}.",
                    },
                },
            )

        # ── 3. Upload original image to S3 ─────────────────────────────────────
        try:
            original_url = s3_service.upload_creation_original(
                file_bytes=image_bytes,
                user_id=current_user.id,
                content_type=image.content_type,
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": {"code": "S3_UPLOAD_ERROR", "message": f"Failed to upload original image: {str(e)}"}},
            )

        # ── 4. Build final prompt ──────────────────────────────────────────────
        final_prompt = gemini_service.build_final_prompt(
            prompt_template=style.prompt_template,
            mood=mood,
            weather=weather,
            dress_style=dress_style,
            custom_prompt=custom_prompt,
            negative_prompt=style.negative_prompt,
        )

        # ── 5. Call Gemini ─────────────────────────────────────────────────────
        try:
            generated_bytes, processing_time = gemini_service.transform_image(
                image_bytes=image_bytes,
                image_mime=image.content_type,
                prompt=final_prompt,
                model="models/gemini-3-pro-image-preview",
            )
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"success": False, "error": {"code": "AI_SERVICE_ERROR", "message": f"AI generation failed: {str(e)}"}},
            )

        # ── 6. Upload generated image to S3 ───────────────────────────────────
        try:
            generated_url = s3_service.upload_creation_generated(
                file_bytes=generated_bytes,
                user_id=current_user.id,
                content_type="image/jpeg",
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": {"code": "S3_UPLOAD_ERROR", "message": f"Failed to upload generated image: {str(e)}"}},
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

        # ── 8. Deduct credits (daily, then main) & increment style usage ───────
        # Ensure user is attached to this session
        current_user = db.merge(current_user)

        credits_to_deduct = style.credits_required

        # Use daily credits first
        if (current_user.daily_credits or 0) > 0:
            use_from_daily = min(current_user.daily_credits, credits_to_deduct)
            current_user.daily_credits -= use_from_daily
            credits_to_deduct -= use_from_daily

        # Deduct any remaining from main credits balance
        if credits_to_deduct > 0:
            current_user.credits -= credits_to_deduct

        style.uses_count += 1

        db.commit()
        db.refresh(creation)
        db.refresh(current_user)

        return GenerateResponse(
            success=True,
            data=_creation_to_out(creation, credits_remaining=current_user.credits),
            message="Image generated successfully!",
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}},
        )


# ─── My Creations ─────────────────────────────────────────────────────────────

@router.get("/mine")
def my_creations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the current user's creation history (newest first)."""
    # Get true total count before pagination
    total_count = db.query(Creation).filter(
        Creation.user_id == current_user.id,
        Creation.is_deleted == False
    ).count()

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

    # Get liked creations to set is_liked correctly
    liked_ids = {
        like.creation_id for like in db.query(CreationLike.creation_id)
        .filter(CreationLike.user_id == current_user.id)
        .all()
    }

    data = [
        _creation_to_out(
            c, 
            credits_remaining=current_user.credits, 
            is_liked=(c.id in liked_ids)
        ) for c in creations
    ]
    return {"success": True, "data": data, "total": total_count}


# ─── Community Feed ───────────────────────────────────────────────────────────

@router.get("/liked")
def liked_creations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a paginated list of all creations liked by the current user."""
    # Subquery to find IDs of liked creations
    query = (
        db.query(Creation)
        .join(CreationLike)
        .filter(CreationLike.user_id == current_user.id, Creation.is_deleted == False)
    )
    
    total_count = query.count()
    
    creations = (
        query
        .options(
            joinedload(Creation.style).joinedload(Style.category),
            joinedload(Creation.user)
        )
        .order_by(CreationLike.created_at.desc()) # Newest likes first
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Since we are fetching from 'liked' table, is_liked is implicitly true for all these
    data = [_creation_to_out(c, is_liked=True) for c in creations]
    return {"success": True, "data": data, "total": total_count}


@router.get("/feed")
def get_community_feed(
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Returns public creations sorted by most recent first.
    If user_id is provided, returns only public creations from that user.
    """
    # Get true total count before pagination
    query = db.query(Creation).filter(Creation.is_public == True, Creation.is_deleted == False)
    
    if user_id:
        query = query.filter(Creation.user_id == user_id)
        
    total_count = query.count()

    creations = (
        query
        .options(
            joinedload(Creation.style).joinedload(Style.category),
            joinedload(Creation.user)
        )
        .order_by(Creation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Get liked creations if user is logged in
    liked_ids = set()
    if current_user:
        liked_ids = {
            like.creation_id for like in db.query(CreationLike.creation_id)
            .filter(CreationLike.user_id == current_user.id)
            .all()
        }

    data = [_creation_to_out(c, is_liked=(c.id in liked_ids)) for c in creations]
    return {"success": True, "data": data, "total": total_count}


# ─── Interactions ─────────────────────────────────────────────────────────────

@router.post("/{creation_id}/like")
def like_creation(
    creation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Increments the like count for a specific creation (only once per user).
    """
    creation = db.query(Creation).filter(Creation.id == creation_id, Creation.is_deleted == False).first()
    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found")

    # Check if user already liked this
    existing_like = db.query(CreationLike).filter(
        CreationLike.user_id == current_user.id,
        CreationLike.creation_id == creation_id
    ).first()

    if existing_like:
        return {
            "success": False,
            "message": "You have already liked this creation",
            "likes_count": creation.likes_count
        }

    # Record the like
    new_like = CreationLike(user_id=current_user.id, creation_id=creation_id)
    db.add(new_like)

    # Increment count
    creation.likes_count = (creation.likes_count or 0) + 1
    db.commit()
    db.refresh(creation)

    return {
        "success": True,
        "message": "Liked successfully",
        "likes_count": creation.likes_count
    }


@router.delete("/{creation_id}/like")
def unlike_creation(
    creation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Removes the current user's like from a specific creation.
    Decrements the like count by 1. Returns 400 if the user hasn't liked it.
    """
    creation = db.query(Creation).filter(Creation.id == creation_id, Creation.is_deleted == False).first()
    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found")

    # Find the existing like record
    existing_like = db.query(CreationLike).filter(
        CreationLike.user_id == current_user.id,
        CreationLike.creation_id == creation_id
    ).first()

    if not existing_like:
        return {
            "success": False,
            "message": "You have not liked this creation",
            "likes_count": creation.likes_count or 0,
            "is_liked": False
        }

    # Remove the like record and decrement count (floor at 0)
    db.delete(existing_like)
    creation.likes_count = max(0, (creation.likes_count or 1) - 1)
    db.commit()
    db.refresh(creation)

    return {
        "success": True,
        "message": "Like removed successfully",
        "likes_count": creation.likes_count,
        "is_liked": False
    }


@router.get("/{creation_id}", response_model=CreationOut)
def get_creation_detail(
    creation_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Returns the details of a single creation if:
    1. It is public, OR
    2. The requester is the owner.
    """
    creation = (
        db.query(Creation)
        .options(joinedload(Creation.style).joinedload(Style.category), joinedload(Creation.user))
        .filter(Creation.id == creation_id, Creation.is_deleted == False)
        .first()
    )

    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found")

    # Privacy check
    is_owner = current_user and current_user.id == creation.user_id
    if not creation.is_public and not is_owner:
        raise HTTPException(status_code=403, detail="This creation is private")

    # Check if liked (same logic as feed)
    is_liked = False
    if current_user:
        is_liked = db.query(CreationLike).filter(
            CreationLike.user_id == current_user.id,
            CreationLike.creation_id == creation.id
        ).first() is not None

    return _creation_to_out(
        creation, 
        credits_remaining=current_user.credits if is_owner else None,
        is_liked=is_liked
    )


@router.patch("/{creation_id}/visibility")
def update_creation_visibility(
    creation_id: int,
    is_public: bool = Form(..., description="Set to true to make public, false to make private"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows a user to toggle their own creation between public and private."""
    creation = db.query(Creation).filter(
        Creation.id == creation_id,
        Creation.user_id == current_user.id,
        Creation.is_deleted == False
    ).first()

    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found or you don't have permission")

    creation.is_public = is_public
    db.commit()

    return {
        "success": True,
        "message": f"Creation visibility updated to {'public' if is_public else 'private'}",
        "is_public": creation.is_public
    }
