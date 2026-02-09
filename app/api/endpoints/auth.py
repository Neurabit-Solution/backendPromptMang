from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.admin import Admin, User
from app.schemas.admin import AdminLogin, AdminLoginResponse, AdminUserResponse
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=AdminLoginResponse)
def login(
    db: Session = Depends(get_db),
    login_data: AdminLogin = None
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
