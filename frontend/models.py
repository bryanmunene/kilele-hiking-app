"""
Database models for Streamlit app
Copied from backend with Streamlit-specific optimizations
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Hike(Base):
    __tablename__ = "hikes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    elevation_gain_m = Column(Float)
    estimated_duration_hours = Column(Float)
    description = Column(Text)
    trail_type = Column(String)
    best_season = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("Review", back_populates="hike", cascade="all, delete-orphan")
    sessions = relationship("HikeSession", back_populates="hike")
    bookmarks = relationship("Bookmark", back_populates="hike")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    bio = Column(Text)
    profile_picture = Column(String)
    experience_level = Column(String, default="Beginner")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    two_factor_secret = Column(String)
    two_factor_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = relationship("Review", back_populates="user")
    sessions = relationship("HikeSession", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following")
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String)
    comment = Column(Text)
    photos = Column(JSON)
    difficulty_rating = Column(String)
    trail_condition = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    hike = relationship("Hike", back_populates="reviews")

class HikeSession(Base):
    __tablename__ = "hike_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hike_id = Column(Integer, ForeignKey("hikes.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    duration_hours = Column(Float)
    distance_covered_km = Column(Float)
    elevation_gain_m = Column(Float)
    status = Column(String, default="in_progress")
    route_data = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    hike = relationship("Hike", back_populates="sessions")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    hike = relationship("Hike", back_populates="bookmarks")

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)
    points = Column(Integer, default=0)
    requirement_type = Column(String, nullable=False)
    requirement_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participants = relationship("ConversationParticipant", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation")

class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="participants")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")

class SessionToken(Base):
    __tablename__ = "session_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)

class TrailComment(Base):
    __tablename__ = "trail_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("trail_comments.id"))  # For replies
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hike = relationship("Hike")
    user = relationship("User")
    replies = relationship("TrailComment", remote_side=[id])

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    goal_type = Column(String)  # distance, elevation, hikes_count, duration
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    deadline = Column(DateTime)
    status = Column(String, default="active")  # active, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    relation = Column(String)  # Changed from 'relationship' to avoid collision
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class TrailCondition(Base):
    __tablename__ = "trail_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    condition = Column(String, nullable=False)  # excellent, good, fair, poor, closed
    weather = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hike = relationship("Hike")
    user = relationship("User")

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    item_name = Column(String, nullable=False)
    category = Column(String)  # clothing, gear, safety, food
    is_required = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hike = relationship("Hike")
