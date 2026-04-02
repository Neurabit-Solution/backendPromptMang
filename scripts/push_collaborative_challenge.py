#!/usr/bin/env python3
"""
Create and push a new Collaborative Canvas challenge.
Usage:
    python scripts/push_collaborative_challenge.py path/to/image.jpg --name "Challenge Name" --desc "Description" --prompt "Prompt"
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
from app.models.user import User  # Ensure User is loaded
from app.models.style import Challenge, Creation, CreationLike

def push_collaborative_challenge(image_path: str, name: str, description: str, prompt: str, day_number: int, group_id: int, duration_days: int):
    # 1. Read and Upload Image (if local path)
    target_url = image_path
    if Path(image_path).exists():
        print(f"Reading image from {image_path}...")
        path = Path(image_path)
        image_bytes = path.read_bytes()
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type:
            mime_type = "image/jpeg"

        print("Uploading target image to S3...")
        try:
            target_url = s3_service.upload_challenge_target_image(image_bytes, name, mime_type)
            print(f"Target image uploaded: {target_url}")
        except Exception as e:
            print(f"FAILED to upload to S3: {e}")
            return
    else:
        print(f"Warning: Local image file not found at {image_path}. Using it as a direct URL if possible.")

    db = SessionLocal()
    try:
        # 2. Cleanup previous collaborative challenges
        print("Cleaning up all previous collaborative challenges...")
        
        # Get IDs of collaborative challenges
        collab_challenges = db.query(Challenge).filter(Challenge.challenge_type == 'collaborative').all()
        collab_challenge_ids = [c.id for c in collab_challenges]
        
        if collab_challenge_ids:
            # 1. Nullify winners to break FK cycles
            db.query(Challenge).filter(Challenge.id.in_(collab_challenge_ids)).update({"previous_winner_id": None}, synchronize_session=False)
            db.commit()

            # 2. Delete related creations and likes
            creations_to_del = db.query(Creation).filter(Creation.challenge_id.in_(collab_challenge_ids)).all()
            creation_ids = [cr.id for cr in creations_to_del]
            
            if creation_ids:
                db.query(CreationLike).filter(CreationLike.creation_id.in_(creation_ids)).delete(synchronize_session=False)
                db.query(Creation).filter(Creation.id.in_(creation_ids)).delete(synchronize_session=False)
                print(f"  Deleted {len(creation_ids)} related creations/submissions.")

            # 3. Delete the challenges themselves
            db.query(Challenge).filter(Challenge.id.in_(collab_challenge_ids)).delete(synchronize_session=False)
            db.commit()
            print(f"  Deleted {len(collab_challenge_ids)} previous collaborative challenge(s).")
        else:
            print("  No previous collaborative challenges found to delete.")

        # 3. Create the new challenge
        now = datetime.now(timezone.utc)
        ends_at = now + timedelta(days=duration_days)
        
        print(f"Creating new collaborative challenge '{name}' in database...")
        challenge = Challenge(
            name=name,
            description=description,
            target_image_url=target_url,
            prompt_template=prompt,
            challenge_type='collaborative',
            day_number=day_number,
            group_id=group_id,
            is_active=True,
            starts_at=now,
            ends_at=ends_at
        )
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        
        print(f"SUCCESS: Collaborative challenge '{name}' pushed successfully!")
        print(f"  ID: {challenge.id}")
        print(f"  Target Image URL: {challenge.target_image_url}")
        print(f"  Day Number: {challenge.day_number}")
        print(f"  Group ID: {challenge.group_id}")
        print(f"  Ends at: {challenge.ends_at}")

    except Exception as e:
        db.rollback()
        print(f"FAILED to update database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push a new Collaborative Canvas challenge.")
    parser.add_argument("image", type=str, help="Path to the local target image.")
    parser.add_argument("--name", type=str, required=True, help="Name of the challenge.")
    parser.add_argument("--desc", type=str, required=True, help="Challenge description.")
    parser.add_argument("--prompt", type=str, required=True, help="AI prompt template.")
    parser.add_argument("--day", type=int, default=1, help="Day number in the story (1-7).")
    parser.add_argument("--group", type=int, default=1, help="Group ID for the 7-day story.")
    parser.add_argument("--days", type=int, default=1, help="Duration in days.")

    args = parser.parse_args()
    
    push_collaborative_challenge(args.image, args.name, args.desc, args.prompt, args.day, args.group, args.days)
