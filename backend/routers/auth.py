from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pyotp
import qrcode
import io
import base64
from pathlib import Path
import shutil
import uuid

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from schemas.two_fa import (
    TwoFASetupRequest, TwoFASetupResponse, TwoFAVerifyRequest,
    TwoFALoginRequest, TwoFADisableRequest
)
from auth import get_password_hash, verify_password, create_access_token, get_current_active_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if username exists
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
        
        # Check if email exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=get_password_hash(user.password)
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"REGISTRATION ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    # Find user
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users (authenticated users only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user profile picture"""
    # Validate file type
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file extension as fallback
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File must be an image (jpg, jpeg, png, gif, or webp)")
    
    # Generate unique filename
    unique_filename = f"{current_user.username}_{uuid.uuid4()}{file_extension}"
    file_path = Path("static/profile_pictures") / unique_filename
    
    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user profile
    current_user.profile_picture = f"/static/profile_pictures/{unique_filename}"
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture": current_user.profile_picture
    }

@router.post("/2fa/setup", response_model=TwoFASetupResponse)
def setup_two_fa(
    request: TwoFASetupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Setup 2FA for user account"""
    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Generate secret
    secret = pyotp.random_base32()
    
    # Create provisioning URI for QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name="Kilele Hiking App"
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Store secret temporarily (will be enabled after verification)
    current_user.two_fa_secret = secret
    db.commit()
    
    return {
        "secret": secret,
        "qr_code_url": f"data:image/png;base64,{img_str}",
        "manual_entry_key": secret
    }

@router.post("/2fa/verify")
def verify_two_fa(
    request: TwoFAVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify 2FA token and enable 2FA"""
    if not current_user.two_fa_secret:
        raise HTTPException(status_code=400, detail="2FA not set up. Please set up 2FA first.")
    
    # Verify token
    totp = pyotp.TOTP(current_user.two_fa_secret)
    if not totp.verify(request.token):
        raise HTTPException(status_code=400, detail="Invalid 2FA token")
    
    # Enable 2FA
    current_user.two_fa_enabled = True
    db.commit()
    
    return {"message": "2FA enabled successfully", "two_fa_enabled": True}

@router.post("/2fa/disable")
def disable_two_fa(
    request: TwoFADisableRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA for user account"""
    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Verify 2FA token
    if current_user.two_fa_enabled and current_user.two_fa_secret:
        totp = pyotp.TOTP(current_user.two_fa_secret)
        if not totp.verify(request.two_fa_token):
            raise HTTPException(status_code=400, detail="Invalid 2FA token")
    
    # Disable 2FA
    current_user.two_fa_enabled = False
    current_user.two_fa_secret = None
    db.commit()
    
    return {"message": "2FA disabled successfully", "two_fa_enabled": False}

@router.post("/login-2fa", response_model=Token)
def login_with_two_fa(user_data: TwoFALoginRequest, db: Session = Depends(get_db)):
    """Login with 2FA token"""
    # Find user
    db_user = db.query(User).filter(User.username == user_data.username).first()
    
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify 2FA token if enabled
    if db_user.two_fa_enabled:
        if not db_user.two_fa_secret:
            raise HTTPException(status_code=400, detail="2FA configuration error")
        
        totp = pyotp.TOTP(db_user.two_fa_secret)
        if not totp.verify(user_data.two_fa_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Update last login
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }
