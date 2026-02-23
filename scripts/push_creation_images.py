#!/usr/bin/env python3
"""
Push creation images to S3 and create a Creation record for user manu1@gmail.com.

Reads two local image files (before = original, after = generated), uploads them
to S3 under creations/originals/<user_id>/ and creations/generated/<user_id>/,
then inserts a Creation row with the returned URLs.

Usage (run from project root):
    python scripts/push_creation_images.py <path_to_original_image> <path_to_generated_image>

Example:
    python scripts/push_creation_images.py ./before.jpg ./after.jpg

Supported image types: .jpg, .jpeg, .png, .webp
"""

import argparse
import mimetypes
import sys
from pathlib import Path

# Allow importing app when run as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core import s3 as s3_service
from app.models.user import User
from app.models.style import Style, Creation


def get_content_type(path: Path) -> str:
    """Guess MIME type from file path/extension."""
    guessed = mimetypes.guess_type(str(path))[0]
    if guessed and guessed.startswith("image/"):
        return guessed
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return "image/jpeg"


def main():
    parser = argparse.ArgumentParser(
        description="Push creation images to S3 and create a Creation record for manu1@gmail.com"
    )
    parser.add_argument(
        "original",
        type=Path,
        help="Path to the original image (before prompt / user upload)",
    )
    parser.add_argument(
        "generated",
        type=Path,
        help="Path to the generated image (after creation)",
    )
    parser.add_argument(
        "--style-id",
        type=int,
        default=None,
        help="Style ID to attach to the creation (default: first active style)",
    )
    args = parser.parse_args()

    for name, p in [("original", args.original), ("generated", args.generated)]:
        if not p.exists():
            print(f"Error: {name} image not found: {p}")
            sys.exit(1)
        if not p.is_file():
            print(f"Error: {name} path is not a file: {p}")
            sys.exit(1)

    db = SessionLocal()
    try:
        # Get user by email
        user = db.query(User).filter(User.email == "manu1@gmail.com").first()
        if not user:
            print("Error: User with email manu1@gmail.com not found.")
            sys.exit(1)

        # Resolve style_id
        style_id = args.style_id
        if style_id is None:
            style = db.query(Style).filter(Style.is_active == True).order_by(Style.id.asc()).first()
            if not style:
                print("Error: No active style found. Create styles first or pass --style-id.")
                sys.exit(1)
            style_id = style.id
        else:
            style = db.query(Style).filter(Style.id == style_id).first()
            if not style:
                print(f"Error: Style with id {style_id} not found.")
                sys.exit(1)

        # Read and upload original image
        original_path = args.original.resolve()
        original_bytes = original_path.read_bytes()
        original_ct = get_content_type(original_path)
        print(f"Uploading original image ({len(original_bytes)} bytes, {original_ct})...")
        original_url = s3_service.upload_creation_original(
            file_bytes=original_bytes,
            user_id=user.id,
            content_type=original_ct,
        )
        print(f"  -> {original_url}")

        # Read and upload generated image
        generated_path = args.generated.resolve()
        generated_bytes = generated_path.read_bytes()
        generated_ct = get_content_type(generated_path)
        print(f"Uploading generated image ({len(generated_bytes)} bytes, {generated_ct})...")
        generated_url = s3_service.upload_creation_generated(
            file_bytes=generated_bytes,
            user_id=user.id,
            content_type=generated_ct,
        )
        print(f"  -> {generated_url}")

        # Create DB record (prompt_used is NOT NULL in DB; use placeholder for manual uploads)
        creation = Creation(
            user_id=user.id,
            style_id=style_id,
            original_image_url=original_url,
            generated_image_url=generated_url,
            thumbnail_url=generated_url,
            prompt_used="(manual upload)",
            credits_used=style.credits_required,
            is_public=True,
        )
        db.add(creation)
        db.commit()
        db.refresh(creation)
        print(f"Created Creation id={creation.id} for user {user.email} (user_id={user.id}), style_id={style_id}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
