from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    referral_code: Optional[str] = None

# Properties to return via API
class User(UserBase):
    id: int
    avatar_url: Optional[str] = None
    credits: int
    is_verified: bool
    referral_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Properties for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_info: Optional[dict] = None

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    
class SignupResponse(BaseModel):
    success: bool
    data: dict
    message: str
