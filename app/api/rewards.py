from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core import database
from ..core.config import settings
from ..api.auth import get_current_user, get_db
from ..models import user as user_models
from ..models import rewards as reward_models
from ..schemas import rewards as reward_schemas
from datetime import date

router = APIRouter(
    prefix="/rewards",
    tags=["Rewards"]
)

@router.post("/admob", response_model=reward_schemas.AdRewardResponse)
def reward_admob_watch(
    ad_data: reward_schemas.AdRewardRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    """
    Award credits to a user after they watch a rewarded ad.
    The frontend should call this after the AdMob callback 'onUserEarnedReward'.
    """
    # 1. Check daily limit
    today = date.today()
    ad_count = db.query(reward_models.AdWatch).filter(
        reward_models.AdWatch.user_id == current_user.id,
        reward_models.AdWatch.watched_date == today
    ).count()

    if ad_count >= settings.DAILY_AD_WATCH_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Daily ad watch limit ({settings.DAILY_AD_WATCH_LIMIT}) reached. Come back tomorrow!"
        )

    # 2. Update user credits
    reward_amount = settings.REWARDED_AD_CREDITS
    current_user.credits += reward_amount
    
    # 3. Create AdWatch record
    new_watch = reward_models.AdWatch(
        user_id=current_user.id,
        ad_unit_id=ad_data.ad_unit_id,
        credits_earned=reward_amount,
        watched_date=today
    )
    db.add(new_watch)

    # 4. Create CreditTransaction record
    new_tx = reward_models.CreditTransaction(
        user_id=current_user.id,
        amount=reward_amount,
        type="ad_watch",
        description=f"Watched ad: {ad_data.ad_unit_id}",
        reference_id=ad_data.ad_unit_id,
        balance_after=current_user.credits
    )
    db.add(new_tx)

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "data": {
            "credits_earned": reward_amount,
            "new_balance": current_user.credits,
            "daily_ad_count": ad_count + 1
        },
        "message": f"Successfully earned {reward_amount} credit!"
    }
