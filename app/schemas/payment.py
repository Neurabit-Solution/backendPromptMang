from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
