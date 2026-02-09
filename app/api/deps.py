from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core import security
from app.models.admin import Admin, User
from app.schemas.admin import TokenPayload

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_admin(
    db: Session = Depends(get_db), token: str = Depends(reuseable_oauth)
) -> Admin:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    admin = db.query(Admin).filter(Admin.id == token_data.sub).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    if not admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive admin")
    
    return admin

def require_permission(permission: str):
    def decorator(current_admin: Admin = Depends(get_current_admin)):
        if current_admin.role == "super_admin":
            return current_admin
        if permission not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_admin
    return decorator
