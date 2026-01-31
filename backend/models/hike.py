from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Hike(Base):
    __tablename__ = "hikes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    location = Column(String(200), nullable=False)
    difficulty = Column(String(50), nullable=False)  # Easy, Moderate, Hard, Extreme
    distance_km = Column(Float, nullable=False)
    elevation_gain_m = Column(Float)
    estimated_duration_hours = Column(Float, nullable=False)
    description = Column(Text)
    trail_type = Column(String(100))  # Loop, Out and Back, Point to Point
    best_season = Column(String(200))  # e.g., "June-September, December-February"
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reviews = relationship("Review", back_populates="hike")
    bookmarks = relationship("Bookmark", back_populates="hike")
    equipment = relationship("Equipment", back_populates="hike")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "difficulty": self.difficulty,
            "distance_km": self.distance_km,
            "elevation_gain_m": self.elevation_gain_m,
            "estimated_duration_hours": self.estimated_duration_hours,
            "description": self.description,
            "trail_type": self.trail_type,
            "best_season": self.best_season,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
