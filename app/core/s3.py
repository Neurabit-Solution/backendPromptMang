"""
S3 Service — handles all image uploads for MagicPic.

Bucket folder structure
-----------------------
magicpic-bucket/
├── styles/
│   └── thumbnails/              ← style preview cards (uploaded by admin service)
│       └── <slug>.jpg
└── creations/
    ├── originals/               ← user's raw uploaded photo
    │   └── <user_id>/<uuid>.jpg
    └── generated/               ← AI-transformed result
        └── <user_id>/<uuid>.jpg
"""

import boto3
import uuid
import io
from botocore.exceptions import ClientError
from app.core.config import settings


def _get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def upload_style_thumbnail(file_bytes: bytes, slug: str, content_type: str = "image/jpeg") -> str:
    """
    Upload a style thumbnail image.
    S3 key: styles/thumbnails/<slug>.jpg
    Returns the public HTTPS URL.
    """
    s3 = _get_s3_client()
    ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
    key = f"styles/thumbnails/{slug}.{ext}"

    s3.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return _build_url(key)


def upload_creation_original(file_bytes: bytes, user_id: int, content_type: str = "image/jpeg") -> str:
    """
    Upload the user's original photo before AI transformation.
    S3 key: creations/originals/<user_id>/<uuid>.jpg
    Returns the S3 URL.
    """
    s3 = _get_s3_client()
    ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
    key = f"creations/originals/{user_id}/{uuid.uuid4()}.{ext}"

    s3.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return _build_url(key)


def upload_creation_generated(file_bytes: bytes, user_id: int, content_type: str = "image/jpeg") -> str:
    """
    Upload the AI-generated result image.
    S3 key: creations/generated/<user_id>/<uuid>.jpg
    Returns the S3 URL.
    """
    s3 = _get_s3_client()
    ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
    key = f"creations/generated/{user_id}/{uuid.uuid4()}.{ext}"

    s3.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return _build_url(key)


def _build_url(key: str) -> str:
    """Build the public HTTPS URL for an S3 object."""
    return f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
