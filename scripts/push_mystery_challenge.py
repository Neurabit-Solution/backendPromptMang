#!/usr/bin/env python3
"""
Create and push a new Mystery Prompt challenge with a target image from local storage.
Usage:
    python scripts/push_mystery_challenge.py path/to/image.jpg --name "Challenge Name" --desc "Description" --prompt "Prompt template"
"""

import sys
import argparse
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Allow importing app when run as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core import s3 as s3_service
from app.models import user  # noqa: F401
from app.models.style import Challenge

def push_mystery_challenge(image_path: str, name: str, description: str, prompt: str, duration_days: int):
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image file not found at {image_path}")
        return

    # 1. Read image data
    print(f"Reading image from {image_path}...")
    image_bytes = path.read_bytes()
    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        mime_type = "image/jpeg"

    # 2. Upload to S3
    print("Uploading target image to S3...")
    try:
        target_url = s3_service.upload_challenge_target_image(image_bytes, name, mime_type)
        print(f"Target image uploaded: {target_url}")
    except Exception as e:
        print(f"FAILED to upload to S3: {e}")
        return

    # 3. Create challenge record
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        ends_at = now + timedelta(days=duration_days)
        
        print(f"Creating challenge '{name}' in database...")
        challenge = Challenge(
            name=name,
            description=description,
            target_image_url=target_url,
            prompt_template=prompt,
            challenge_type='mystery',
            is_active=True,
            starts_at=now,
            ends_at=ends_at
        )
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        
        print(f"SUCCESS: Challenge '{name}' pushed successfully!")
        print(f"  ID: {challenge.id}")
        print(f"  Target URL: {challenge.target_image_url}")
        print(f"  Ends at: {challenge.ends_at}")

    except Exception as e:
        db.rollback()
        print(f"FAILED to update database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push a new Mystery Prompt challenge.")
    parser.add_argument("image", type=str, help="Path to the target image (local file).")
    parser.add_argument("--name", type=str, required=True, help="Name of the challenge.")
    parser.add_argument("--desc", type=str, required=True, help="Description for users.")
    parser.add_argument("--prompt", type=str, required=True, help="Hidden prompt template for generation.")
    parser.add_argument("--days", type=int, default=1, help="Duration of the challenge in days (default: 1).")

    args = parser.parse_args()
    
    push_mystery_challenge(args.image, args.name, args.desc, args.prompt, args.days)
