from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.admin import Admin, User
from app.schemas.admin import AdminLogin, AdminLoginResponse, AdminUserResponse
from app.core import security
from app.core.config import settings
from app.schemas.admin import AdminLogin, AdminLoginResponse, AdminUserResponse, AdminCreate
import uuid

router = APIRouter()

@router.post("/login", response_model=AdminLoginResponse)
def login(
    db: Session = Depends(get_db),
    login_data: AdminLogin = Body(...)
) -> Any:
    # 1. Check user exists
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        return {
            "success": False,
            "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
        }
    
    # 2. Check password
    if not security.verify_password(login_data.password, user.hashed_password):
        return {
            "success": False,
            "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
        }
    
    # 3. Check if user is admin
    admin = db.query(Admin).filter(Admin.user_id == user.id).first()
    if not admin:
        return {
            "success": False,
            "error": {"code": "NOT_ADMIN", "message": "You do not have admin privileges"}
        }
    
    if not admin.is_active:
        return {
            "success": False,
            "error": {"code": "ADMIN_INACTIVE", "message": "Admin account is deactivated"}
        }

    # 4. Generate token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        admin.id, role=admin.role, expires_delta=access_token_expires
    )

    return {
        "success": True,
        "data": {
            "admin": {
                "id": admin.id,
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "role": admin.role,
                "permissions": admin.permissions,
                "created_at": admin.created_at,
                "last_login": admin.last_login
            },
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    }

@router.post("/register", response_model=AdminLoginResponse)
def register(
    db: Session = Depends(get_db),
    admin_in: AdminCreate = Body(...)
) -> Any:
    # 1. Check if user already exists
    user = db.query(User).filter(User.email == admin_in.email).first()
    if user:
        return {
            "success": False,
            "error": {"code": "EMAIL_EXISTS", "message": "Email already registered"}
        }
    
    # 2. Create User
    ref_code = str(uuid.uuid4())[:8].upper()
    db_user = User(
        email=admin_in.email,
        hashed_password=security.get_password_hash(admin_in.password),
        name=admin_in.name,
        referral_code=ref_code,
        is_verified=True,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 3. Create Admin
    # For now, let's assign permissions based on role
    permissions = []
    if admin_in.role == "super_admin":
        permissions = ["all"]
    elif admin_in.role == "admin":
        permissions = ["users.view", "users.create", "credits.manage", "styles.manage"]
    
    db_admin = Admin(
        user_id=db_user.id,
        role=admin_in.role,
        permissions=permissions,
        is_active=True
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    # 4. Generate token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        db_admin.id, role=db_admin.role, expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "data": {
            "admin": {
                "id": db_admin.id,
                "user_id": db_user.id,
                "email": db_user.email,
                "name": db_user.name,
                "avatar_url": db_user.avatar_url,
                "role": db_admin.role,
                "permissions": db_admin.permissions,
                "created_at": db_admin.created_at,
                "last_login": db_admin.last_login
            },
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    }
