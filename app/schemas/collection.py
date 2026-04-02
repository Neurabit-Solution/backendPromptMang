from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.style import CreationOut

# ─── Collection ─────────────────────────────────────────────────────────────

class CollectionBase(BaseModel):
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None

class CollectionCreate(CollectionBase):
    pass

class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None

class CollectionOut(CollectionBase):
    id: int
    user_id: int
    creations_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CollectionDetailOut(CollectionOut):
    creations: List[CreationOut]

class CollectionListResponse(BaseModel):
    success: bool = True
    data: List[CollectionOut]
    total: int

class CollectionItemAction(BaseModel):
    creation_id: int
