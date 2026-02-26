from fastapi import APIRouter, Depends, UploadFile, File, Form, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core import gemini as gemini_service
from app.models.style import Style, GuestUsage

router = APIRouter(prefix="/guest", tags=["Guest (Free Trial)"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

@router.post("/generate")
async def guest_generate(
    device_id: str = Form(..., description="Unique ID of the device"),
    style_id: int = Form(..., description="ID of the style to apply"),
    image: UploadFile = File(..., description="User's photo (JPG/PNG, max 10 MB)"),
    db: Session = Depends(get_db),
):
    """
    Apply a style to an image for a non-authenticated user.
    Strictly limited to one use per device_id.
    Does not save images to S3; returns the generated image bytes directly.
    """
    try:
        # 1. Check if device has already used its free trial
        usage = db.query(GuestUsage).filter(GuestUsage.device_id == device_id).first()
        if usage:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "success": False,
                    "error": {
                        "code": "TRIAL_EXHAUSTED",
                        "message": "Your free trial has ended. Please sign up or log in to continue creating!"
                    }
                }
            )

        # 2. Validate image
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

        # 3. Find style
        style = db.query(Style).filter(Style.id == style_id, Style.is_active == True).first()
        if not style:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": {"code": "STYLE_NOT_FOUND", "message": "Style not found."}},
            )

        # 4. Build prompt (minimal version for guest)
        final_prompt = gemini_service.build_final_prompt(
            prompt_template=style.prompt_template,
            mood=None,
            weather=None,
            dress_style=None,
            custom_prompt=None,
        )

        # 5. Call Gemini
        try:
            generated_bytes, _ = gemini_service.transform_image(
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

        # 6. Mark device as used
        new_usage = GuestUsage(
            device_id=device_id,
            style_id=style_id
        )
        db.add(new_usage)
        
        # Increment style usage count even for guest
        style.uses_count += 1
        
        db.commit()

        # 7. Return image bytes directly
        return Response(content=generated_bytes, media_type="image/jpeg")

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}},
        )
