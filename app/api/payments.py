import razorpay
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hmac
import hashlib

from app.core.database import get_db
from app.api.auth import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.payment import Transaction
from app.schemas.payment import (
    OrderCreateRequest,
    OrderCreateResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
    PricingInfoResponse,
)

router = APIRouter(prefix="/payments", tags=["Payments"])

# Initialize Razorpay client
if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
else:
    razorpay_client = None

@router.get("/pricing", response_model=PricingInfoResponse)
def get_pricing():
    """
    Returns the credits package size and price from configuration.
    """
    total_price = settings.CREDITS_PACKAGE_SIZE * settings.CREDIT_PRICE_INR
    return PricingInfoResponse(
        credits=settings.CREDITS_PACKAGE_SIZE,
        price_inr=total_price,
        currency="INR"
    )

@router.post("/create-order", response_model=OrderCreateResponse)
def create_order(
    request: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Razorpay order before initiating payment on the frontend.
    Uses the fixed credits package size from config.
    """
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment gateway is not configured."
        )

    # Use the credits package size from config instead of request for consistency with user request
    credits_to_buy = settings.CREDITS_PACKAGE_SIZE
    
    amount_inr = credits_to_buy * settings.CREDIT_PRICE_INR
    # Razorpay amount is in paise (1 INR = 100 paise)
    amount_paise = int(amount_inr * 100)

    try:
        data = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"receipt_{current_user.id}_{int(credits_to_buy)}",
            "notes": {
                "user_id": current_user.id,
                "credits": credits_to_buy
            }
        }
        order = razorpay_client.order.create(data=data)

        # Store the order in DB
        transaction = Transaction(
            user_id=current_user.id,
            order_id=order["id"],
            amount_inr=amount_inr,
            credits_purchased=credits_to_buy,
            status="created"
        )
        db.add(transaction)
        db.commit()

        return OrderCreateResponse(
            success=True,
            order_id=order["id"],
            amount=amount_inr,
            currency="INR",
            key_id=settings.RAZORPAY_KEY_ID
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )

@router.post("/verify-payment", response_model=PaymentVerifyResponse)
def verify_payment(
    request: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verifies the payment via Razorpay signature and grants credits.
    """
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment gateway is not configured."
        )

    transaction = db.query(Transaction).filter(
        Transaction.order_id == request.razorpay_order_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found."
        )

    if transaction.status == "success":
        return PaymentVerifyResponse(
            success=True,
            message="Payment already verified and credits granted.",
            credits_added=0,
            total_credits=current_user.credits
        )

    try:
        # Verify Payment Signature
        params_dict = {
            'razorpay_order_id': request.razorpay_order_id,
            'razorpay_payment_id': request.razorpay_payment_id,
            'razorpay_signature': request.razorpay_signature
        }
        # This will raise a SignatureVerificationError if verification fails
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Payment is valid
        transaction.status = "success"
        transaction.payment_id = request.razorpay_payment_id
        transaction.signature = request.razorpay_signature
        
        # Grant credits to the user
        current_user.credits += transaction.credits_purchased
        
        db.commit()

        return PaymentVerifyResponse(
            success=True,
            message=f"Successfully added {transaction.credits_purchased} credits.",
            credits_added=transaction.credits_purchased,
            total_credits=current_user.credits
        )

    except razorpay.errors.SignatureVerificationError:
        transaction.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}"
        )
