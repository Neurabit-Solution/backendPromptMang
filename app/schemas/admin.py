from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    role: Optional[str] = None

# Admin Schemas
class AdminBase(BaseModel):
    role: str
    is_active: bool = True
    permissions: List[str] = []

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminUserResponse(BaseModel):
    id: int
    user_id: int
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    role: str
    permissions: List[str]
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminLoginResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Any] = None

class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "admin"

# User Schemas for Admin
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str] = None
    credits: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    credits: int = 2500
    is_verified: bool = True
    is_active: bool = True
