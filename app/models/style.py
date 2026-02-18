from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float,
    ForeignKey, JSON, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Category(Base):
    """
    Groups styles into logical buckets shown in the UI
    (e.g. "Trending", "Anime", "Traditional", "Fantasy").
    """
    __tablename__ = "categories"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100), unique=True, nullable=False)
    slug         = Column(String(100), unique=True, index=True, nullable=False)
    icon         = Column(String(10), nullable=True)          # emoji or icon name
    description  = Column(String(200), nullable=True)
    preview_url  = Column(String(500), nullable=True)         # S3 URL for category cover
    display_order= Column(Integer, default=0)
    is_active    = Column(Boolean, default=True)

    # Relationships
    styles = relationship("Style", back_populates="category")


class Style(Base):
    """
    Each row is one "filter card" the user sees on the home screen
    (e.g. Ghibli Art, Red Saree, Neon Glow).

    S3 path for thumbnail:  styles/thumbnails/<slug>.jpg
    The full URL is stored in preview_url.
    """
    __tablename__ = "styles"

    id               = Column(Integer, primary_key=True, index=True)
    category_id      = Column(Integer, ForeignKey("categories.id"), index=True, nullable=False)

    name             = Column(String(100), index=True, nullable=False)
    slug             = Column(String(100), unique=True, index=True, nullable=False)
    description      = Column(String(500), nullable=True)

    # S3 URL of the thumbnail image shown on the style card
    preview_url      = Column(String(500), nullable=False)

    # --- AI Prompt ---
    # Full prompt template sent to Gemini when this style is selected.
    # Example: "Transform this photo into a Studio Ghibli anime illustration..."
    prompt_template  = Column(Text, nullable=False)

    # What the AI should avoid (optional)
    negative_prompt  = Column(Text, nullable=True)

    # Metadata / discovery
    tags             = Column(JSON, default=list)   # ["anime", "artistic", "colorful"]
    credits_required = Column(Integer, default=50)

    # Stats (auto-incremented on each use)
    uses_count       = Column(Integer, default=0)

    # Visibility flags
    is_trending      = Column(Boolean, default=False)
    is_new           = Column(Boolean, default=True)
    is_active        = Column(Boolean, default=True)
    display_order    = Column(Integer, default=0)

    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category   = relationship("Category", back_populates="styles")
    creations  = relationship("Creation", back_populates="style")


class Creation(Base):
    """
    One row per AI generation attempt by a user.

    S3 paths:
      Original image  →  creations/originals/<user_id>/<uuid>.jpg
      Generated image →  creations/generated/<user_id>/<uuid>.jpg

    The full S3 URLs are stored in original_image_url and generated_image_url.
    """
    __tablename__ = "creations"

    id                   = Column(Integer, primary_key=True, index=True)
    user_id              = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    style_id             = Column(Integer, ForeignKey("styles.id"), index=True, nullable=False)

    # --- S3 Image URLs ---
    original_image_url   = Column(String(500), nullable=False)   # user's uploaded photo
    generated_image_url  = Column(String(500), nullable=True)    # AI result (null until done)
    thumbnail_url        = Column(String(500), nullable=True)    # smaller version of result

    # --- Generation options chosen by user ---
    mood                 = Column(String(50), nullable=True)     # happy / sad / romantic …
    weather              = Column(String(50), nullable=True)     # sunny / rainy / snowy …
    dress_style          = Column(String(50), nullable=True)     # casual / formal / fantasy …
    custom_prompt        = Column(String(200), nullable=True)    # extra text from user

    # --- Audit / Debug ---
    # The exact final prompt that was sent to Gemini (template + user inputs merged)
    prompt_used          = Column(Text, nullable=True)
    credits_used         = Column(Integer, default=50)
    processing_time      = Column(Float, nullable=True)          # seconds Gemini took

    # --- Stats ---
    likes_count          = Column(Integer, default=0)
    views_count          = Column(Integer, default=0)

    # --- Status ---
    is_public            = Column(Boolean, default=True)
    is_featured          = Column(Boolean, default=False)
    is_deleted           = Column(Boolean, default=False)        # soft-delete

    created_at           = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user   = relationship("User", back_populates="creations")
    style  = relationship("Style", back_populates="creations")
