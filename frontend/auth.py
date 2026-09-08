"""
Authentication module for Streamlit app
Simplified auth using session state with persistent tokens
Persists login across browser refreshes using localStorage
"""
import streamlit as st
import streamlit.components.v1 as components
import bcrypt
import pyotp
import secrets
from pathlib import Path
from database import get_db
from models import User, SessionToken
from datetime import datetime, timedelta

_session_storage = components.declare_component(
    "kilele_session_storage", path=str(Path(__file__).parent / "session_storage")
)

def hash_password(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if len(plain_password.encode('utf-8')) > 72:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def create_session_token(user_id: int, remember_me: bool = True) -> str:
    """Create a persistent session token for user"""
    with get_db() as db:
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=30 if remember_me else 1)
        
        # Save token to database
        session_token = SessionToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(session_token)
        db.flush()
        
        return token

def get_user_by_token(token: str) -> dict:
    """Get user data from session token"""
    with get_db() as db:
        session = db.query(SessionToken).filter(
            SessionToken.token == token,
            SessionToken.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Update last used timestamp
        session.last_used = datetime.utcnow()
        db.flush()
        
        user = db.query(User).filter(User.id == session.user_id).first()
        if not user or not user.is_active:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture,
            "is_admin": user.is_admin,
            "two_factor_enabled": user.two_factor_enabled,
            "two_factor_secret": user.two_factor_secret,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

def invalidate_token(token: str):
    """Invalidate a session token (for logout)"""
    with get_db() as db:
        session = db.query(SessionToken).filter(SessionToken.token == token).first()
        if session:
            db.delete(session)
            db.flush()

def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user and return user data"""
    with get_db() as db:
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture,
            "is_admin": user.is_admin,
            "two_factor_enabled": user.two_factor_enabled,
            "two_factor_secret": user.two_factor_secret,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

def register_user(username: str, email: str, password: str, full_name: str = None) -> dict:
    """Register a new user"""
    with get_db() as db:
        # Check if user exists
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            raise ValueError("Username or email already exists")
        
        # Create new user
        hashed_pw = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_pw,
            full_name=full_name
        )
        db.add(new_user)
        db.flush()
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name
        }

def setup_2fa(user_id: int) -> tuple:
    """Setup 2FA for user and return secret + provisioning URI"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Generate secret if not exists
        if not user.two_factor_secret:
            secret = pyotp.random_base32()
            user.two_factor_secret = secret
            db.commit()
        else:
            secret = user.two_factor_secret
        
        # Generate provisioning URI for QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="Kilele Hiking App"
        )
        
        return secret, provisioning_uri

def verify_2fa_code(user_id: int, code: str) -> bool:
    """Verify a 2FA code"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.two_factor_secret:
            return False
        
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(code)

def enable_2fa(user_id: int, enable: bool = True) -> bool:
    """Enable or disable 2FA for a user"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.two_factor_enabled = enable
        db.commit()
        return True

def disable_2fa(user_id: int) -> bool:
    """Disable 2FA and remove secret"""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.two_factor_enabled = False
        user.two_factor_secret = None
        db.commit()
        return True

def is_authenticated() -> bool:
    """Check if user is authenticated (checks session state and persistent token)"""
    # First check session state
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return True
    
    # Check for persistent token
    if "session_token" in st.session_state and st.session_state.session_token:
        user_data = get_user_by_token(st.session_state.session_token)
        if user_data:
            # Restore session
            st.session_state.authenticated = True
            st.session_state.user = user_data
            return True
        else:
            # Invalid/expired token
            if "session_token" in st.session_state:
                del st.session_state.session_token
    
    return False

def get_current_user() -> dict:
    """Get current authenticated user"""
    if is_authenticated():
        return st.session_state.user
    return None

def logout():
    """Logout current user and invalidate session token"""
    # Invalidate token in database
    if "session_token" in st.session_state and st.session_state.session_token:
        invalidate_token(st.session_state.session_token)
    
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user = None
    if "session_token" in st.session_state:
        del st.session_state.session_token
    st.session_state.clear()
    st.session_state.storage_operation = "clear"

def save_token_to_browser(token: str):
    """Save session token to browser localStorage for persistent login"""
    st.session_state.storage_operation = "write"
    st.session_state.storage_token = token

def restore_session_from_storage():
    """Use a bidirectional component; components.html cannot return a token."""
    if st.session_state.get("authenticated") and st.session_state.get("session_token"):
        current = get_user_by_token(st.session_state.session_token)
        if current:
            st.session_state.user = current
        else:
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.pop("session_token", None)
            st.session_state.storage_operation = "clear"
    operation = st.session_state.get("storage_operation", "read")
    result = _session_storage(
        operation=operation,
        token=st.session_state.get("storage_token", ""),
        key="session_storage",
        default=None,
    )
    if not isinstance(result, dict) or result.get("operation") != operation:
        return
    if operation != "read":
        st.session_state.pop("storage_operation", None)
        st.session_state.pop("storage_token", None)
        return
    token = result.get("token")
    if token and not st.session_state.get("authenticated"):
        st.session_state.session_token = token
        is_authenticated()

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("⚠️ Please login to access this page")
            st.stop()
        return func(*args, **kwargs)
    return wrapper
