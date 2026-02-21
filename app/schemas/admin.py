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
    is_verified: bool = True
    is_active: bool = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    icon: str
    description: str
    display_order: int = 0
    is_active: bool = True

class CategoryCreate(CategoryBase):
    slug: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    slug: str
    preview_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Style Schemas
class StyleBase(BaseModel):
    category_id: int
    name: str
    description: str
    prompt_template: str
    negative_prompt: Optional[str] = None
    tags: List[str] = []
    credits_required: int = 50
    display_order: int = 0
    is_trending: bool = False
    is_new: bool = True
    is_active: bool = True

class StyleCreate(StyleBase):
    pass

class StyleUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_template: Optional[str] = None
    negative_prompt: Optional[str] = None
    tags: Optional[List[str]] = None
    credits_required: Optional[int] = None
    display_order: Optional[int] = None
    is_trending: Optional[bool] = None
    is_new: Optional[bool] = None
    is_active: Optional[bool] = None

class StyleResponse(StyleBase):
    id: int
    preview_url: str
    uses_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
