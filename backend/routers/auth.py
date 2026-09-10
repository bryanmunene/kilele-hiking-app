"""Account entry points using the same security rules as Streamlit."""
import base64
import io
from datetime import datetime

import pyotp
import qrcode
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_active_user, get_current_admin
from database import get_db
from kilele_core.security import (
    authenticate, hash_password, set_two_factor, throttle, two_factor_state,
    verify_password, verify_second_factor, TooManyAttempts, TwoFactorRequired,
)
from kilele_core.images import image_data_url
from models.user import User
from models.session_token import SessionToken
from rate_limiter import limiter
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from schemas.two_fa import TwoFASetupRequest, TwoFASetupResponse, TwoFAVerifyRequest, TwoFALoginRequest, TwoFADisableRequest

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/hour")
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    try:
        throttle(db, "register", str(user.email), limit=3)
        if db.query(User).filter((User.username == user.username) | (func.lower(User.email) == str(user.email).lower())).first():
            raise HTTPException(409, "Username or email already registered")
        record = User(username=user.username.strip(), email=str(user.email).lower(),
            full_name=user.full_name, hashed_password=hash_password(user.password))
        db.add(record)
        db.flush()
        from kilele_core.operations import enqueue
        enqueue(db, f"welcome:{record.id}", record.id, "welcome")
        db.commit()
        db.refresh(record)
        return record
    except TooManyAttempts as exc:
        raise HTTPException(429, str(exc)) from None
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username or email already registered") from None


def _login(db, username, password, code):
    try:
        record = authenticate(db, User, username, password, code)
    except TooManyAttempts as exc:
        raise HTTPException(429, str(exc)) from None
    except TwoFactorRequired as exc:
        raise HTTPException(401, str(exc)) from None
    if not record:
        raise HTTPException(401, "Invalid credentials or authenticator code")
    db.commit()
    return {"access_token": create_access_token({"sub": record.username}), "token_type": "bearer", "user": record}


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    return _login(db, user.username, user.password, user.two_fa_token)


@router.post("/login-2fa", response_model=Token)
@limiter.limit("10/minute")
def login_with_two_fa(request: Request, user_data: TwoFALoginRequest, db: Session = Depends(get_db)):
    return _login(db, user_data.username, user_data.password, user_data.two_fa_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_admin)):
    return db.query(User).offset(max(0, skip)).limit(max(1, min(limit, 100))).all()


@router.post("/upload-profile-picture")
@limiter.limit("10/hour")
async def upload_profile_picture(request: Request, file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    try:
        current_user.profile_picture = image_data_url(await file.read(5 * 1024 * 1024 + 1))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    finally:
        await file.close()
    db.commit()
    return {"message": "Profile picture updated", "profile_picture": current_user.profile_picture}


def _revoke_sessions(db, user):
    user.password_changed_at = datetime.utcnow()
    db.query(SessionToken).filter_by(user_id=user.id).delete()


@router.post("/2fa/setup", response_model=TwoFASetupResponse)
@limiter.limit("5/minute")
def setup_two_fa(request: Request, body: TwoFASetupRequest,
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    if two_factor_state(current_user)[0]:
        raise HTTPException(409, "Disable the existing authenticator before replacing it")
    secret = pyotp.random_base32()
    set_two_factor(current_user, False, secret)
    db.commit()
    uri = pyotp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="Kilele Hiking App")
    buffer = io.BytesIO()
    qrcode.make(uri).save(buffer, format="PNG")
    return {"secret": secret, "manual_entry_key": secret,
            "qr_code_url": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()}


@router.post("/2fa/verify")
@limiter.limit("5/minute")
def verify_two_fa(request: Request, body: TwoFAVerifyRequest,
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not verify_second_factor(current_user, body.token, required_only=False):
        raise HTTPException(401, "Invalid authenticator code")
    set_two_factor(current_user, True, current_user.two_factor_secret or current_user.two_fa_secret)
    _revoke_sessions(db, current_user)
    db.commit()
    return {"message": "Authenticator enabled. Sign in again.", "two_fa_enabled": True}


@router.post("/2fa/disable")
@limiter.limit("5/minute")
def disable_two_fa(request: Request, body: TwoFADisableRequest,
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not verify_password(body.password, current_user.hashed_password) or not verify_second_factor(current_user, body.two_fa_token):
        raise HTTPException(401, "Invalid credentials or authenticator code")
    set_two_factor(current_user, False, None)
    _revoke_sessions(db, current_user)
    db.commit()
    return {"message": "Authenticator disabled. Sign in again.", "two_fa_enabled": False}
