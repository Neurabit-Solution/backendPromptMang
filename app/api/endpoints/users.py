from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.api.deps import get_current_admin, require_permission
from app.models.admin import User, Admin
from app.schemas.admin import UserResponse, UserCreate
from app.core import security
import uuid

router = APIRouter()

@router.get("/", response_model=dict)
def get_users(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_permission("users.view")),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    is_verified: Optional[bool] = None,
    is_active: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Any:
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Sorting
    if sort_order == "desc":
        query = query.order_by(getattr(User, sort_by).desc())
    else:
        query = query.order_by(getattr(User, sort_by).asc())
        
    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "success": True,
        "data": {
            "users": [UserResponse.model_validate(u).model_dump() for u in users],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit,
                "has_next": page * limit < total,
                "has_prev": page > 1
            }
        }
    }

@router.post("/", response_model=dict)
def create_user(
    *,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_permission("users.create")),
    user_in: UserCreate
) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="The user with this email already exists")
    
    # Mock referral code generation
    ref_code = str(uuid.uuid4())[:8].upper()
    
    db_user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        name=user_in.name,
        phone=user_in.phone,
        credits=user_in.credits,
        is_verified=user_in.is_verified,
        is_active=user_in.is_active,
        referral_code=ref_code
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "success": True,
        "data": {"user": UserResponse.model_validate(db_user).model_dump()},
        "message": "User created successfully"
    }
