from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class StravaToken(Base):
    """Store Strava OAuth tokens per user"""
    __tablename__ = "strava_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)  # When access token expires
    athlete_id = Column(Integer, nullable=False)  # Strava athlete ID
    scope = Column(String(500))  # Permissions granted
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_synced = Column(DateTime)  # Last successful sync
    sync_enabled = Column(Boolean, default=True)  # Auto-sync toggle
    
    # Relationship
    user = relationship("User", back_populates="strava_token")
    activities = relationship("StravaActivity", back_populates="token", cascade="all, delete-orphan")


class StravaActivity(Base):
    """Store synced Strava activities"""
    __tablename__ = "strava_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("strava_tokens.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    hike_session_id = Column(Integer, ForeignKey("hike_sessions.id"), nullable=True)  # Link to our hike session
    
    # Strava data
    strava_activity_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255))
    activity_type = Column(String(50))  # Hike, Walk, Run, etc.
    distance = Column(Float)  # meters
    moving_time = Column(Integer)  # seconds
    elapsed_time = Column(Integer)  # seconds
    total_elevation_gain = Column(Float)  # meters
    start_date = Column(DateTime)
    start_date_local = Column(DateTime)
    
    # Location data
    start_latlng = Column(String(100))  # "[lat, lng]"
    end_latlng = Column(String(100))
    map_summary_polyline = Column(Text)  # Encoded polyline
    
    # Stats
    average_speed = Column(Float)  # m/s
    max_speed = Column(Float)  # m/s
    average_heartrate = Column(Float)
    max_heartrate = Column(Float)
    calories = Column(Float)
    
    # Social
    achievement_count = Column(Integer, default=0)
    kudos_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    photo_count = Column(Integer, default=0)
    
    # Metadata
    imported_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_matched_to_trail = Column(Boolean, default=False)  # Matched to our Hike model
    matched_hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=True)
    
    # Relationships
    token = relationship("StravaToken", back_populates="activities")
    user = relationship("User")
    hike_session = relationship("HikeSession", back_populates="strava_activity")
    matched_hike = relationship("Hike")


class StravaWebhookSubscription(Base):
    """Track webhook subscription status"""
    __tablename__ = "strava_webhook_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, unique=True)  # From Strava
    callback_url = Column(String(500))
    verify_token = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
