
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timezone

from app.core.database import get_db
from app.core import security, s3 as s3_service, gemini as gemini_service
from app.models.user import User
from app.schemas.style import CreationOut, ChallengeOut, ChallengeLeaderboardEntry, StoryStep
from app.core.config import settings

router = APIRouter(prefix="/challenges", tags=["Challenges"])

# --- Auth helper ---
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

def _refresh_daily_credits(user: User, db: Session) -> User:
    now = datetime.now(timezone.utc)
    today = now.date()

    if user.daily_credits_date is None or user.daily_credits_date.date() != today:
        user.daily_credits = settings.DAILY_FREE_CREDITS
        user.daily_credits_date = now
        user = db.merge(user)
        db.commit()
        db.refresh(user)

    return user

# --- Endpoints ---

@router.get("/current", response_model=ChallengeOut)
def get_current_challenge(db: Session = Depends(get_db)):
    """Return the currently active challenge (if any)."""
    now = datetime.now(timezone.utc)
    challenge = (
        db.query(Challenge)
        .filter(Challenge.is_active == True, Challenge.starts_at <= now, Challenge.ends_at >= now)
        .order_by(Challenge.challenge_type.desc()) # Prefer collaborative if both active?
        .first()
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="No active challenge found.")
    return challenge


@router.get("/collaborative/current", response_model=ChallengeOut)
def get_current_collaborative_challenge(db: Session = Depends(get_db)):
    """Return the currently active collaborative story challenge."""
    now = datetime.now(timezone.utc)
    challenge = (
        db.query(Challenge)
        .filter(
            Challenge.challenge_type == "collaborative",
            Challenge.is_active == True,
            Challenge.starts_at <= now,
            Challenge.ends_at >= now
        )
        .first()
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="No active collaborative challenge found.")
    return challenge


@router.get("/collaborative/story/{group_id}", response_model=List[StoryStep])
def get_story_progress(group_id: int, db: Session = Depends(get_db)):
    """Returns the sequence of winners for a 7-day story challenge."""
    challenges = (
        db.query(Challenge)
        .options(joinedload(Challenge.winner).joinedload(Creation.user))
        .filter(Challenge.group_id == group_id)
        .order_by(Challenge.day_number.asc())
        .all()
    )
    
    steps = []
    for c in challenges:
        if c.winner:
            steps.append(StoryStep(
                day=c.day_number,
                image_url=c.winner.generated_image_url,
                winner_name=c.winner.user.name if c.winner.user else "Anonymous",
                likes=c.winner.likes_count or 0
            ))
    return steps


@router.post("/{challenge_id}/submit")
async def submit_challenge_entry(
    challenge_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Participate in a challenge:
    1. Generate image using user's photo + challenge's hidden prompt.
    2. Upload result to S3.
    3. Calculate similarity score with the challenge's target image.
    4. Save as a special 'Creation' tied to the challenge.
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.is_active == True).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    now = datetime.now(timezone.utc)
    if challenge.ends_at < now:
        raise HTTPException(status_code=400, detail="This challenge has expired.")

    # 1. Image checks
    image_bytes = await image.read()
    
    # 2. Credit deduction (fixed cost for challenges, e.g. 1 credit)
    current_user = _refresh_daily_credits(current_user, db)
    total_creds = (current_user.credits or 0) + (current_user.daily_credits or 0)
    
    cost = 1 # Challenges are cheap!
    if total_creds < cost:
        raise HTTPException(status_code=402, detail="Insufficient credits to join challenge.")

    # 3. AI Transformation
    try:
        generated_bytes, proc_time = gemini_service.transform_image(
            image_bytes=image_bytes,
            image_mime=image.content_type,
            prompt=challenge.prompt_template
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI transformation failed: {e}")

    # 4. S3 Uploads
    orig_url = s3_service.upload_creation_original(image_bytes, current_user.id, image.content_type)
    gen_url = s3_service.upload_creation_generated(generated_bytes, current_user.id, "image/jpeg")

    # 5. Scoring
    score = 0
    if challenge.challenge_type == "mystery":
        # Gemini Similarity Scoring (The Magic for Mystery Prompt!)
        score = gemini_service.calculate_similarity(generated_bytes, challenge.target_image_url)
    else:
        # For collaborative, maybe we just give a base score or use a different metric
        # but for now let's keep it 0 or use similarity if the prompt is to "match" the style
        score = gemini_service.calculate_similarity(generated_bytes, challenge.target_image_url)

    # 6. Save Creation
    creation = Creation(
        user_id=current_user.id,
        style_id=1, # Default style or generic 'challenge' style
        challenge_id=challenge.id,
        original_image_url=orig_url,
        generated_image_url=gen_url,
        thumbnail_url=gen_url,
        prompt_used=challenge.prompt_template,
        similarity_score=score,
        credits_used=cost,
        processing_time=proc_time
    )
    db.add(creation)

    # Deduct credits
    current_user = db.merge(current_user)
    if (current_user.daily_credits or 0) >= cost:
        current_user.daily_credits -= cost
    else:
        current_user.credits -= cost
        
    db.commit()
    db.refresh(creation)

    return {
        "success": True,
        "data": {
            "id": creation.id,
            "similarity_score": score,
            "generated_image_url": gen_url,
            "message": f"Submitted successfully! Match score: {score}%"
        }
    }


@router.get("/{challenge_id}/leaderboard", response_model=List[ChallengeLeaderboardEntry])
def get_challenge_leaderboard(challenge_id: int, db: Session = Depends(get_db)):
    """Returns top matching results for the challenge."""
    results = (
        db.query(Creation)
        .options(joinedload(Creation.user))
        .filter(Creation.challenge_id == challenge_id)
        .order_by(Creation.similarity_score.desc())
        .limit(20)
        .all()
    )
    
    return [
        ChallengeLeaderboardEntry(
            id=c.id,
            user_name=c.user.name if c.user else "Anonymous",
            avatar_url=c.user.avatar_url if c.user else None,
            similarity_score=c.similarity_score or 0,
            generated_image_url=c.generated_image_url,
            created_at=c.created_at
        ) for c in results
    ]


@router.post("/{challenge_id}/set_winner")
def admin_set_challenge_winner(
    challenge_id: int,
    creation_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user) # Should check for admin role
):
    """
    Manually set the winner for a day (for the story progress).
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    
    creation = db.query(Creation).filter(Creation.id == creation_id).first()
    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found.")
    
    challenge.previous_winner_id = creation_id
    db.commit()
    
    return {"success": True, "message": "Winner set successfully."}
