from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdRewardRequest(BaseModel):
    ad_unit_id: Optional[str] = "rewarded_ad_main"
    platform: Optional[str] = "android"

class AdRewardResponseData(BaseModel):
    credits_earned: int
    new_balance: int
    daily_ad_count: int

class AdRewardResponse(BaseModel):
    success: bool
    data: Optional[AdRewardResponseData] = None
    message: str
    error: Optional[dict] = None
