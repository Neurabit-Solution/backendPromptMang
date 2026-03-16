from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core import security, database
from ..core.config import settings
from ..core.firebase import verify_firebase_android_token, get_firebase_status
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


def get_current_user(
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Requires Bearer access token. Returns the authenticated user."""
    payload = security.verify_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


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

    # Generate unique referral code for this new user
    referral_code = generate_referral_code()
    while db.query(models.User).filter(models.User.referral_code == referral_code).first():
        referral_code = generate_referral_code()

    # Handle referral if a valid referral_code was supplied
    referred_by = None
    if user.referral_code:
        referred_by = (
            db.query(models.User)
            .filter(models.User.referral_code == user.referral_code)
            .first()
        )

    new_user = models.User(
        email=email,
        hashed_password=hashed_password,
        name=user.name,
        phone=user.phone,
        referral_code=referral_code,
        credits=settings.SIGNUP_INITIAL_CREDITS,
        is_verified=False,
        referred_by_id=referred_by.id if referred_by else None,
        last_login=func.now(),
    )

    # Reward the referrer, if any
    if referred_by:
        referred_by.credits += settings.REFERRAL_REWARD_CREDITS
        db.add(referred_by)

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
    Only accepts tokens originating from the Android app.
    """
    # Enforce Android-only: reject requests that declare a non-android platform
    platform = (google_data.platform or "").lower().strip()
    if platform and platform != "android":
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "error": {
                    "code": "PLATFORM_NOT_ALLOWED",
                    "message": "Google sign-in is only supported on the Android app.",
                },
            },
        )

    try:
        decoded_token = verify_firebase_android_token(google_data.id_token)
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
    referral_code_input = google_data.referral_code

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

        # Lookup referrer if referral code was supplied
        referred_by = None
        if referral_code_input:
            referred_by = (
                db.query(models.User)
                .filter(models.User.referral_code == referral_code_input)
                .first()
            )

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
            credits=settings.SIGNUP_INITIAL_CREDITS,
            is_verified=True,
            referred_by_id=referred_by.id if referred_by else None,
            last_login=func.now(),
        )

        if referred_by:
            referred_by.credits += settings.REFERRAL_REWARD_CREDITS
            db.add(referred_by)

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
        
        user.last_login = func.now()
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
        
    user.last_login = func.now()
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
            "expires_in": 1800
        },
        "message": "Login successful"
    }

@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Return the current authenticated user (e.g. profile, referral_code, credits).
    Use this so logged-in users can view their referral code and balance anytime.
    """
    return {
        "success": True,
        "data": {"user": current_user},
        "message": "OK",
    }


@router.put("/profile")
def update_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information (name, phone, avatar_url)."""
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "data": {"user": current_user},
        "message": "Profile updated successfully"
    }


@router.post("/profile/avatar")
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and set a new profile avatar."""
    from ..core import s3
    
    # Validate image
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format (JPG, PNG, WebP only)")
    
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024: # 5MB limit
        raise HTTPException(status_code=413, detail="Image too large (max 5MB)")
    
    # Upload to S3
    avatar_url = s3.upload_avatar(contents, current_user.id, file.content_type)
    
    # Update user record
    current_user.avatar_url = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "data": {"avatar_url": avatar_url},
        "message": "Avatar uploaded successfully"
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

@router.delete("/account")
def delete_account(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete the user account and all associated data.
    This includes:
    1. All creations and their images in S3.
    2. All likes, votes, and battle history.
    3. Credit transactions and ad watch history.
    4. The user profile itself.
    """
    from ..core.s3 import delete_user_objects
    
    user_id = current_user.id
    
    # 1. Delete S3 objects first (optional but good to do before DB record is gone, 
    # though we have user_id from current_user)
    delete_user_objects(user_id)
    
    # 2. Delete user from DB
    # The cascading deletes in the database schema will handle:
    # creations, likes, votes, credit_transactions, ad_watches
    db.delete(current_user)
    db.commit()
    
    return {
        "success": True,
        "message": "Account and all associated data have been permanently deleted."
    }
