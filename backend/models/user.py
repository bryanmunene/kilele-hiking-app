from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    profile_picture = Column(String(255), nullable=True)  # Path to profile picture
    two_fa_enabled = Column(Boolean, default=False)
    two_fa_secret = Column(String(32), nullable=True)  # Secret for 2FA
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    reviews = relationship("Review", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    conversation_participants = relationship("ConversationParticipant", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender")
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "profile_picture": self.profile_picture,
            "two_fa_enabled": self.two_fa_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
