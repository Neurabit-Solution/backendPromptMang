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
    credits_required = Column(Integer, default=1)

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


class Challenge(Base):
    """
    Weekly or daily Mystery Prompt Challenges.
    - Type 'mystery': Users try to match the aesthetic of 'target_image_url'.
    - Type 'collaborative': Community builds a story; winner of day N is inspiration for day N+1.
    """
    __tablename__ = "challenges"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(100), nullable=False)
    description         = Column(Text, nullable=True)
    
    # For 'mystery', this is the image to match.
    # For 'collaborative', this is the previous day's winner image.
    target_image_url    = Column(String(500), nullable=False)
    prompt_template     = Column(Text, nullable=False)
    
    challenge_type      = Column(String(50), default="mystery") # 'mystery', 'collaborative'
    day_number          = Column(Integer, default=1)           # 1-7 for collaborative
    group_id            = Column(Integer, nullable=True)       # unique ID for a 7-day sequence
    previous_winner_id  = Column(Integer, ForeignKey("creations.id", use_alter=True, name="fk_challenge_winner"), nullable=True)

    starts_at           = Column(DateTime(timezone=True), server_default=func.now())
    ends_at             = Column(DateTime(timezone=True), nullable=False)
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    creations = relationship("Creation", back_populates="challenge", foreign_keys="Creation.challenge_id")
    winner    = relationship("Creation", foreign_keys=[previous_winner_id], post_update=True)


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
    credits_used         = Column(Integer, default=1)
    
    # Challenge Link
    challenge_id         = Column(Integer, ForeignKey("challenges.id"), nullable=True)
    similarity_score     = Column(Float, default=0)
    
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
    user       = relationship("User", back_populates="creations")
    style      = relationship("Style", back_populates="creations")
    challenge  = relationship("Challenge", back_populates="creations", foreign_keys=[challenge_id])
    collections = relationship("Collection", secondary="collection_creations", back_populates="creations")


class GuestUsage(Base):
    """
    Tracks one-time free generation for guest users based on device ID.
    Used to prevent device-based trial abuse.
    """
    __tablename__ = "guest_usages"

    id           = Column(Integer, primary_key=True, index=True)
    device_id    = Column(String(100), unique=True, index=True, nullable=False)
    style_id     = Column(Integer, ForeignKey("styles.id"), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


from sqlalchemy import UniqueConstraint

class CreationLike(Base):
    """
    Tracks which user liked which creation to prevent multiple likes.
    """
    __tablename__ = "creation_likes"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    creation_id  = Column(Integer, ForeignKey("creations.id"), index=True, nullable=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    # Ensure one user can only like a creation once
    __table_args__ = (UniqueConstraint('user_id', 'creation_id', name='_user_creation_like_uc'),)


class Collection(Base):
    """
    A named group of creations belonging to a user (like a playlist).
    """
    __tablename__ = "collections"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name         = Column(String(100), nullable=False)
    description  = Column(String(500), nullable=True)
    cover_url    = Column(String(500), nullable=True)

    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user      = relationship("User", back_populates="collections")
    creations = relationship("Creation", secondary="collection_creations", back_populates="collections")


class CollectionCreation(Base):
    """
    Many-to-many relationship mapping creations into collections.
    """
    __tablename__ = "collection_creations"

    id            = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), index=True, nullable=False)
    creation_id   = Column(Integer, ForeignKey("creations.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Ensure a creation can't be added to the same collection twice
    __table_args__ = (UniqueConstraint('collection_id', 'creation_id', name='_col_creation_uc'),)
