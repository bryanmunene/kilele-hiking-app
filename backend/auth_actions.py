"""Token material never persists in plaintext or logs."""
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy import delete
from models.auth_action import AuthActionToken


def issue_action(db, user_id: int, purpose: str, minutes: int = 10) -> str:
    db.execute(delete(AuthActionToken).where(AuthActionToken.expires_at <= datetime.utcnow()))
    token = secrets.token_urlsafe(32)
    db.add(AuthActionToken(
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        user_id=user_id, purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=minutes),
    ))
    db.commit()
    return token


def consume_action(db, token: str, purpose: str, user_id: int | None = None) -> int:
    statement = delete(AuthActionToken).where(
        AuthActionToken.token_hash == hashlib.sha256(token.encode()).hexdigest(),
        AuthActionToken.purpose == purpose,
        AuthActionToken.expires_at > datetime.utcnow(),
    )
    if user_id is not None:
        statement = statement.where(AuthActionToken.user_id == user_id)
    result = db.execute(statement.returning(AuthActionToken.user_id)).scalar_one_or_none()
    if result is None:
        raise ValueError("This link has expired or has already been used. Please start again.")
    return result
