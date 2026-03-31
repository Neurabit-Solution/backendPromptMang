from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from app.core.database import Base

class CreditTransaction(Base):
    """
    Audit log of all credit changes (earnings and expenses).
    """
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for earned, negative for spent
    type = Column(String(50), nullable=False) # signup_bonus, ad_watch, purchase, creation, referral, etc.
    description = Column(String(200), nullable=False)
    reference_id = Column(String(100), nullable=True) # e.g., creation_id or ad_unit_id
    balance_after = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdWatch(Base):
    """
    Tracks ad viewing for daily limit enforcement and audit.
    """
    __tablename__ = "ad_watches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ad_provider = Column(String(50), default="admob")
    ad_unit_id = Column(String(100), nullable=True)
    credits_earned = Column(Integer, default=1)
    watched_date = Column(Date, server_default=func.current_date())
    watched_at = Column(DateTime(timezone=True), server_default=func.now())
