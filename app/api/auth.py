from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core import security, database
from ..core.firebase import verify_firebase_id_token, get_firebase_status
from ..models import user as models
from ..schemas import user as schemas
from datetime import timedelta
import logging
import secrets
import random
import string

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@router.get("/firebase-status")
def firebase_status():
    """Check if Firebase is configured on the server (for debugging deploy)."""
    return get_firebase_status()

@router.post("/signup", response_model=schemas.SignupResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    email = user.email.lower().strip()
    db_user = (
        db.query(models.User)
        .filter(func.lower(models.User.email) == email)
        .first()
    )
    if db_user:
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": {
                    "code": "EMAIL_EXISTS",
                    "message": "An account with this email already exists",
                },
            },
        )
    
    hashed_password = security.get_password_hash(user.password)
    
    # Generate unique referral code
    referral_code = generate_referral_code()
    while db.query(models.User).filter(models.User.referral_code == referral_code).first():
        referral_code = generate_referral_code()
        
    new_user = models.User(
        email=email,
        hashed_password=hashed_password,
        name=user.name,
        phone=user.phone,
        referral_code=referral_code,
        credits=2500, # Initial credits
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = security.create_access_token(new_user.email)
    refresh_token = security.create_refresh_token(new_user.email)
    
    # Construct response to match README
    return {
        "success": True,
        "data": {
            "user": new_user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        },
        "message": "Account created successfully. Please verify your email."
    }


@router.post("/google", response_model=schemas.SignupResponse)
def login_with_google(google_data: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Login or signup using a Firebase Google ID token.
    """
    try:
        decoded_token = verify_firebase_id_token(google_data.id_token)
    except ValueError as e:
        cause = e.__cause__
        logger.warning(
            "Google auth token verification failed: %s",
            str(cause) if cause else str(e),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_GOOGLE_TOKEN",
                    "message": "Google authentication failed. Please try again.",
                },
            },
        )

    email = decoded_token.get("email")
    if not email:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "EMAIL_NOT_PROVIDED",
                    "message": "Google account does not have a valid email.",
                },
            },
        )

    email = email.lower().strip()
    name = decoded_token.get("name") or email.split("@")[0]
    avatar_url = decoded_token.get("picture")

    user = (
        db.query(models.User)
        .filter(func.lower(models.User.email) == email)
        .first()
    )

    if not user:
        # Generate unique referral code
        referral_code = generate_referral_code()
        while db.query(models.User).filter(models.User.referral_code == referral_code).first():
            referral_code = generate_referral_code()

        # Create a random password that is never used directly
        random_password = secrets.token_urlsafe(32)
        hashed_password = security.get_password_hash(random_password)

        user = models.User(
            email=email,
            hashed_password=hashed_password,
            name=name,
            phone=None,
            avatar_url=avatar_url,
            referral_code=referral_code,
            credits=2500,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Ensure the user is marked as verified and update profile info
        updated = False
        if not user.is_verified:
            user.is_verified = True
            updated = True
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            updated = True
        if name and user.name != name:
            user.name = name
            updated = True
        if updated:
            db.commit()
            db.refresh(user)

    access_token = security.create_access_token(user.email)
    refresh_token = security.create_refresh_token(user.email)

    return {
        "success": True,
        "data": {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
        },
        "message": "Login with Google successful",
    }

@router.post("/login", response_model=schemas.SignupResponse)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    email = user_credentials.email.lower().strip()
    user = (
        db.query(models.User)
        .filter(func.lower(models.User.email) == email)
        .first()
    )
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Email or password is incorrect",
                },
            },
        )
    
    if not security.verify_password(user_credentials.password, user.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Email or password is incorrect",
                },
            },
        )
        
    access_token = security.create_access_token(user.email)
    refresh_token = security.create_refresh_token(user.email)
    
    return {
        "success": True,
        "data": {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        },
        "message": "Login successful"
    }

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    # Note: In a real implementation using OAuth2PasswordBearer, the token is extracted from Authorization header.
    # The README says Authorization: Bearer <refresh_token>, so oauth2_scheme handles extraction.
    
    payload = security.verify_token(token)
    if not payload or payload.get("type") != "refresh":
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
        
    access_token = security.create_access_token(user.email)
    # Optionally rotate refresh token
    
    return {
        "access_token": access_token,
        "refresh_token": token, # Return same or new one
        "token_type": "bearer",
        "expires_in": 1800
    }
