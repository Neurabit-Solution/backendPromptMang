#!/usr/bin/env python3
"""
Simple script to clear all collaborative challenges and related submissions.
"""

import sys
from pathlib import Path

# Allow importing app when run as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.user import User  # Ensure User is loaded
from app.models.style import Challenge, Creation, CreationLike

def clear_collab_challenges():
    db = SessionLocal()
    try:
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
            count = db.query(Challenge).filter(Challenge.id.in_(collab_challenge_ids)).delete(synchronize_session=False)
            db.commit()
            print(f"  Deleted {count} previous collaborative challenge(s).")
            print("Cleanup complete.")
        else:
            print("  No collaborative challenges found to clear.")

    except Exception as e:
        db.rollback()
        print(f"FAILED: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_collab_challenges()
