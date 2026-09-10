"""Authentication rules shared by both entry points."""
import hashlib
from datetime import datetime, timedelta

import bcrypt
import pyotp
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, delete

metadata = MetaData()
attempts = Table("auth_attempts", metadata,
    Column("key", String(64), primary_key=True),
    Column("count", Integer, nullable=False),
    Column("expires_at", DateTime, nullable=False))


class TooManyAttempts(ValueError):
    pass


class TwoFactorRequired(ValueError):
    pass


def throttle(db, action, identifier, limit=10, minutes=15):
    """Atomic, database-backed fixed window shared across processes/hosts."""
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    now = datetime.utcnow()
    key = hashlib.sha256(f"{action}:{identifier.casefold()}".encode()).hexdigest()
    db.execute(delete(attempts).where(attempts.c.expires_at <= now))
    insert = sqlite_insert if db.bind.dialect.name == "sqlite" else pg_insert
    statement = insert(attempts).values(key=key, count=1, expires_at=now + timedelta(minutes=minutes))
    count = db.execute(statement.on_conflict_do_update(
        index_elements=[attempts.c.key], set_={"count": attempts.c.count + 1}
    ).returning(attempts.c.count)).scalar_one()
    # Failed authentication must not roll back the attempt counter.
    db.commit()
    if count > limit:
        raise TooManyAttempts("Too many attempts. Please try again in 15 minutes.")


def hash_password(password):
    if not 8 <= len(password) or len(password.encode("utf-8")) > 72:
        raise ValueError("Use at least 8 characters and at most 72 UTF-8 bytes.")
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed):
    try:
        return len(password.encode()) <= 72 and bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, AttributeError):
        return False


def two_factor_state(user):
    # Canonical website fields win; legacy API accounts remain protected.
    if user.two_factor_enabled:
        return True, user.two_factor_secret
    return bool(user.two_fa_enabled), user.two_fa_secret


def set_two_factor(user, enabled, secret):
    user.two_factor_enabled = user.two_fa_enabled = enabled
    user.two_factor_secret = user.two_fa_secret = secret


def verify_second_factor(user, code, required_only=True):
    enabled, secret = two_factor_state(user)
    if required_only and not enabled:
        return True
    secret = secret or user.two_factor_secret or user.two_fa_secret
    try:
        return bool(secret and code and pyotp.TOTP(secret).verify(code))
    except (ValueError, TypeError):
        return False


def authenticate(db, user_model, username, password, code=""):
    username = username.strip()
    throttle(db, "login", username)
    user = db.query(user_model).filter(user_model.username == username).first()
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        return None
    if two_factor_state(user)[0] and not code:
        raise TwoFactorRequired("Enter your authenticator code.")
    if not verify_second_factor(user, code):
        return None
    user.last_login = datetime.utcnow()
    return user


def require_admin(db, user_model, actor_id):
    actor = db.get(user_model, actor_id) if actor_id else None
    if not actor or not actor.is_active or not actor.is_admin:
        raise PermissionError("Administrator access required.")
    return actor
