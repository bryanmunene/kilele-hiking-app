"""Password recovery without exposing whether an account exists."""
from datetime import datetime
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from auth import get_password_hash, get_current_active_user
from auth_actions import consume_action, issue_action
from database import get_db
from email_service import email_service
from models.auth_action import AuthActionToken
from models.user import User
from models.session_token import SessionToken
from rate_limiter import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class RecoveryRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    token: str = Field(min_length=32, max_length=200)
    password: str = Field(min_length=8, max_length=72)


class VerificationRequest(BaseModel):
    token: str = Field(min_length=32, max_length=200)


@router.post("/request-verification")
@limiter.limit("30/minute")
def request_verification(request: Request, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not email_service.configured:
        raise HTTPException(503, "Email sending is not configured yet.")
    if user.email_verified:
        return {"message": "Email already verified."}
    pending = db.query(AuthActionToken).filter_by(user_id=user.id, purpose="email_verify").filter(AuthActionToken.expires_at > datetime.utcnow()).first()
    if not pending:
        token = issue_action(db, user.id, "email_verify", minutes=30)
        if not email_service.send_verification(user.email, token):
            db.query(AuthActionToken).filter_by(token_hash=hashlib.sha256(token.encode()).hexdigest()).delete()
            db.commit()
            raise HTTPException(503, "Email delivery failed. Please try again later.")
    return {"message": "Check your inbox for the verification link."}


@router.post("/verify-email")
@limiter.limit("5/minute")
def verify_email(request: Request, body: VerificationRequest, db: Session = Depends(get_db)):
    try:
        user_id = consume_action(db, body.token, "email_verify")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(400, "Verification link is no longer valid.")
    user.email_verified = True
    db.commit()
    return {"message": "Email verified."}


@router.get("/recovery-status")
def recovery_status():
    return {"available": email_service.configured}


@router.post("/forgot-password")
@limiter.limit("30/minute")
def forgot_password(request: Request, body: RecoveryRequest, db: Session = Depends(get_db)):
    if not email_service.configured:
        raise HTTPException(503, "Email recovery is not available yet. Please contact the administrator.")
    user = db.query(User).filter(func.lower(User.email) == str(body.email).lower(), User.is_active.is_(True)).first()
    if user:
        # Bound mail volume per account even when requests arrive from many addresses.
        pending = db.query(AuthActionToken).filter_by(user_id=user.id, purpose="password_reset").filter(AuthActionToken.expires_at > datetime.utcnow()).first()
        if not pending:
            token = issue_action(db, user.id, "password_reset", minutes=30)
            if not email_service.send_password_reset(user.email, token, user.username):
                db.query(AuthActionToken).filter_by(token_hash=hashlib.sha256(token.encode()).hexdigest()).delete()
                db.commit()
    return {"message": "If an active account matches that address, a password-reset link will be sent."}


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, body: ResetRequest, db: Session = Depends(get_db)):
    if len(body.password.encode("utf-8")) > 72:
        raise HTTPException(422, "Password is too long. Use at most 72 UTF-8 bytes.")
    try:
        user_id = consume_action(db, body.token, "password_reset")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(400, "This reset link is no longer valid.")
    user.hashed_password = get_password_hash(body.password)
    user.password_changed_at = datetime.utcnow()
    db.query(SessionToken).filter_by(user_id=user.id).delete()
    db.query(AuthActionToken).filter_by(user_id=user.id).delete()
    db.commit()
    return {"message": "Password updated. Sign in with your new password."}
