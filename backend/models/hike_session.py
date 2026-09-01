from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class HikeSession(Base):
    """Track active and completed hikes by users"""
    __tablename__ = "hike_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    
    # Session tracking
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    status = Column(String(30), default="in_progress")
    
    # Progress tracking
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    distance_covered_km = Column(Float, default=0.0)
    duration_minutes = Column(Integer, default=0)
    duration_hours = Column(Float, default=0.0)
    elevation_gain_m = Column(Float, default=0.0)
    route_data = Column(Text, nullable=True)
    
    # Notes and rating
    notes = Column(String(500), nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Relationship to Strava activity
    strava_activity = relationship("StravaActivity", back_populates="hike_session", uselist=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "hike_id": self.hike_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "is_active": self.is_active,
            "status": self.status,
            "current_latitude": self.current_latitude,
            "current_longitude": self.current_longitude,
            "distance_covered_km": self.distance_covered_km,
            "duration_minutes": self.duration_minutes,
            "duration_hours": self.duration_hours,
            "elevation_gain_m": self.elevation_gain_m,
            "route_data": self.route_data,
            "notes": self.notes,
            "rating": self.rating
        }


class SavedHike(Base):
    """User's saved/favorite hikes"""
    __tablename__ = "saved_hikes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "hike_id": self.hike_id,
            "saved_at": self.saved_at.isoformat() if self.saved_at else None
        }
