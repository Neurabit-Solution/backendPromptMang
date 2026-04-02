from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.api.creations import get_current_user, _creation_to_out, get_optional_user
from app.models.user import User
from app.models.style import Creation, Collection, CollectionCreation, CreationLike
from app.schemas.collection import (
    CollectionCreate, CollectionUpdate, CollectionOut, 
    CollectionDetailOut, CollectionListResponse, CollectionItemAction
)

router = APIRouter(prefix="/collections", tags=["Collections"])

# ─── CRUD Collections ─────────────────────────────────────────────────────────

@router.post("", response_model=CollectionOut)
def create_collection(
    collection: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new empty collection for the user."""
    new_col = Collection(
        user_id=current_user.id,
        name=collection.name,
        description=collection.description,
        cover_url=collection.cover_url
    )
    db.add(new_col)
    db.commit()
    db.refresh(new_col)
    return new_col

@router.get("", response_model=CollectionListResponse)
def list_my_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns all collections owned by the current user."""
    collections = (
        db.query(Collection)
        .filter(Collection.user_id == current_user.id)
        .order_by(Collection.updated_at.desc(), Collection.created_at.desc())
        .all()
    )
    
    # Calculate counts manually or via subquery
    result = []
    for col in collections:
        count = db.query(CollectionCreation).filter(CollectionCreation.collection_id == col.id).count()
        col_out = CollectionOut.model_validate(col)
        col_out.creations_count = count
        result.append(col_out)

    return {"success": True, "data": result, "total": len(result)}

@router.get("/{collection_id}", response_model=CollectionDetailOut)
def get_collection_detail(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns a collection and all creations inside it."""
    col = db.query(Collection).filter(
        Collection.id == collection_id, 
        Collection.user_id == current_user.id
    ).first()
    
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Get creations with liked state for current user
    liked_ids = {
        like.creation_id for like in db.query(CreationLike.creation_id)
        .filter(CreationLike.user_id == current_user.id)
        .all()
    }

    creations_out = [
        _creation_to_out(c, is_liked=(c.id in liked_ids)) 
        for c in col.creations if not c.is_deleted
    ]

    col_out = CollectionDetailOut.model_validate(col)
    col_out.creations = creations_out
    col_out.creations_count = len(creations_out)
    return col_out

@router.put("/{collection_id}", response_model=CollectionOut)
def update_collection(
    collection_id: int,
    update: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates collection name, description or cover."""
    col = db.query(Collection).filter(
        Collection.id == collection_id, 
        Collection.user_id == current_user.id
    ).first()
    
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")

    if update.name is not None:
        col.name = update.name
    if update.description is not None:
        col.description = update.description
    if update.cover_url is not None:
        col.cover_url = update.cover_url
    
    db.commit()
    db.refresh(col)
    return col

@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a collection (does not delete the actual creations)."""
    col = db.query(Collection).filter(
        Collection.id == collection_id, 
        Collection.user_id == current_user.id
    ).first()
    
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")

    db.delete(col)
    db.commit()
    return {"success": True, "message": "Collection deleted"}

# ─── Collection Items ─────────────────────────────────────────────────────────

@router.post("/{collection_id}/items")
def add_to_collection(
    collection_id: int,
    item: CollectionItemAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adds a creation to a collection."""
    # 1. Verify collection ownership
    col = db.query(Collection).filter(
        Collection.id == collection_id, 
        Collection.user_id == current_user.id
    ).first()
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")

    # 2. Verify creation exists and is not deleted
    creation = db.query(Creation).filter(
        Creation.id == item.creation_id, 
        Creation.is_deleted == False
    ).first()
    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found")

    # 3. Add to link table (ignore if already exists via UniqueConstraint handling or manual check)
    existing = db.query(CollectionCreation).filter(
        CollectionCreation.collection_id == collection_id,
        CollectionCreation.creation_id == item.creation_id
    ).first()

    if not existing:
        link = CollectionCreation(collection_id=collection_id, creation_id=item.creation_id)
        db.add(link)
        db.commit()

    return {"success": True, "message": "Creation added to collection"}

@router.delete("/{collection_id}/items/{creation_id}")
def remove_from_collection(
    collection_id: int,
    creation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Removes a creation from a collection."""
    # 1. Verify collection ownership
    col = db.query(Collection).filter(
        Collection.id == collection_id, 
        Collection.user_id == current_user.id
    ).first()
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")

    # 2. Delete the link
    link = db.query(CollectionCreation).filter(
        CollectionCreation.collection_id == collection_id,
        CollectionCreation.creation_id == creation_id
    ).first()

    if link:
        db.delete(link)
        db.commit()

    return {"success": True, "message": "Creation removed from collection"}
