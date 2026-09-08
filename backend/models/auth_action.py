"""Single-use, expiring tokens for OAuth and password recovery."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from database import Base


class AuthActionToken(Base):
    __tablename__ = "auth_action_tokens"
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    purpose = Column(String(32), nullable=False)
    expires_at = Column(DateTime, nullable=False)
