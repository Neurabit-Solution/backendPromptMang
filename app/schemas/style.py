from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# ─── Category ────────────────────────────────────────────────────────────────

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None
    preview_url: Optional[str] = None
    display_order: int
    styles_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ─── Style ────────────────────────────────────────────────────────────────────

class StyleOut(BaseModel):
    """Returned to the frontend for the style grid / cards."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    preview_url: str          # S3 URL of the thumbnail image
    category: CategoryOut
    uses_count: int
    is_trending: bool
    is_new: bool
    tags: Optional[List[str]] = []
    credits_required: int

    model_config = ConfigDict(from_attributes=True)


class StyleListResponse(BaseModel):
    success: bool = True
    data: List[StyleOut]
    total: int


# ─── Creation (Generate) ─────────────────────────────────────────────────────

class GenerateResponse(BaseModel):
    """Returned after a successful AI image generation."""
    success: bool = True
    data: "CreationOut"
    message: str = "Image generated successfully!"


class CreationOut(BaseModel):
    id: int
    original_image_url: str
    generated_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    style: StyleOut
    mood: Optional[str] = None
    weather: Optional[str] = None
    dress_style: Optional[str] = None
    is_public: bool
    credits_used: int
    credits_remaining: int
    processing_time: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


GenerateResponse.model_rebuild()
