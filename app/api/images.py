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

from app.core.s3 import _get_s3_client
from app.core.config import settings

router = APIRouter(prefix="/images", tags=["Images"])

# Map file extensions to MIME types
MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "gif": "image/gif",
    "svg": "image/svg+xml",
}


@router.get("/{s3_key:path}")
def serve_image(s3_key: str):
    """
    Proxy endpoint that fetches an image from the private S3 bucket
    and serves it directly to the client.

    Usage:
      GET /api/images/styles/thumbnails/oil-painting.png
      GET /api/images/categories/thumbnails/anime.jpg
      GET /api/images/creations/generated/42/abc123.jpg
    """
    s3 = _get_s3_client()

    try:
        response = s3.get_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key,
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="Image not found")
        elif error_code == "AccessDenied":
            raise HTTPException(status_code=403, detail="Access denied to image")
        else:
            raise HTTPException(status_code=500, detail=f"S3 error: {error_code}")

    # Read image bytes
    image_bytes = response["Body"].read()

    # Determine content type from S3 metadata or file extension
    content_type = response.get("ContentType", "application/octet-stream")
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
