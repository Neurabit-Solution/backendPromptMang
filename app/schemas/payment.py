from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class OrderCreateRequest(BaseModel):
    credits: int

class OrderCreateResponse(BaseModel):
    success: bool
    order_id: str
    amount: float
    currency: str
    key_id: str

class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentVerifyResponse(BaseModel):
    success: bool
    message: str
    credits_added: int
    total_credits: int

class PricingInfoResponse(BaseModel):
    credits: int
    price_inr: float
    currency: str

class PaymentHistoryItem(BaseModel):
    id: int
    order_id: str
    payment_id: Optional[str] = None
    amount_inr: float
    credits_purchased: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaymentHistoryResponse(BaseModel):
    success: bool
    history: List[PaymentHistoryItem]
