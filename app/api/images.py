"""
Image Proxy API
---------------
GET /api/images/{s3_key:path}  → fetches image from private S3 and serves it directly

This allows the frontend to use:
  <img src="http://backend:8000/api/images/styles/thumbnails/oil-painting.png" />

The backend uses its AWS credentials to fetch the image, so the S3 bucket
can remain fully private.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from botocore.exceptions import ClientError


import logging
import re
import traceback
from app.core.s3 import get_s3_client
from app.core.config import settings

router = APIRouter(prefix="/images", tags=["Images"])
logger = logging.getLogger(__name__)

# Map file extensions to MIME types
MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "gif": "image/gif",
    "svg": "image/svg+xml",
}


def _normalize_style_thumbnail_key(s3_key: str) -> str:
    """
    Normalize legacy or alternate style thumbnail paths to the canonical S3 key.
    Canonical: styles/thumbnails/<slug>.<ext>
    Handles:   styles/thumbnail/s/<slug>.png or similar variants.
    """
    # Match styles/thumbnail/s/<slug>.<ext> or styles/thumbnail/<slug>.<ext>
    m = re.match(r"^styles/thumbnail(?:s)?/s?/?([^/]+)\.(png|jpg|jpeg|webp)$", s3_key, re.I)
    if m:
        slug, ext = m.group(1), m.group(2).lower()
        if ext == "jpeg":
            ext = "jpg"
        return f"styles/thumbnails/{slug}.{ext}"
    return s3_key


@router.get("/{s3_key:path}")
def serve_image(s3_key: str):
    """
    Proxy endpoint that fetches an image from the private S3 bucket
    and serves it directly to the client.
    """
    s3 = get_s3_client()
    key_to_try = _normalize_style_thumbnail_key(s3_key)
    keys_to_try = [key_to_try]
    if key_to_try != s3_key:
        keys_to_try.append(s3_key)
    # If normalized key is styles/thumbnails/<slug>.png but we usually store .jpg, try .jpg
    if key_to_try.startswith("styles/thumbnails/") and key_to_try.endswith(".png"):
        keys_to_try.append(key_to_try[:-4] + ".jpg")

    response = None
    last_error = None
    for k in keys_to_try:
        try:
            response = s3.get_object(Bucket=settings.AWS_S3_BUCKET, Key=k)
            break
        except ClientError as e:
            last_error = e
            if e.response["Error"]["Code"] != "NoSuchKey":
                break
            continue

    if response is None:
        error_code = last_error.response["Error"]["Code"] if last_error else "NoSuchKey"
        logger.error(f"S3 ClientError for key {s3_key}: {error_code} - {last_error}")
        if error_code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="Image not found")
        if error_code == "AccessDenied":
            raise HTTPException(status_code=403, detail="Access denied to image")
        raise HTTPException(status_code=500, detail=f"S3 error: {error_code}")

    try:
        # Read image bytes
        image_bytes = response["Body"].read()

        # Determine content type from S3 metadata or file extension
        content_type = response.get("ContentType") or "application/octet-stream"
    except Exception as e:
        logger.error(f"Unexpected error serving image {s3_key}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error serving image")

    if content_type == "application/octet-stream":
        ext = s3_key.rsplit(".", 1)[-1].lower() if "." in s3_key else ""
        content_type = MIME_TYPES.get(ext, "application/octet-stream")

    return Response(
        content=image_bytes,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
        },
    )
