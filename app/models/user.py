from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import settings

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    credits = Column(Integer, default=settings.SIGNUP_INITIAL_CREDITS)
    is_verified = Column(Boolean, default=False)
    referral_code = Column(String, unique=True, index=True, nullable=True)
    referred_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    daily_credits = Column(Integer, default=0)
    daily_credits_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creations = relationship("Creation", back_populates="user")
