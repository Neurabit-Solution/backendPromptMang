from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(String, unique=True, index=True, nullable=False)
    payment_id = Column(String, unique=True, index=True, nullable=True)
    signature = Column(String, nullable=True)
    amount_inr = Column(Float, nullable=False)
    credits_purchased = Column(Integer, nullable=False)
    status = Column(String, default="created", index=True) # created, success, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
