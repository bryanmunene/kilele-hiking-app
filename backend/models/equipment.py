"""
Equipment and PlannedHike models
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=True)  # Nullable for general gear catalog
    item_name = Column(String, nullable=False)
    category = Column(String)  # clothing, footwear, safety, navigation, food, camping
    is_required = Column(Boolean, default=False)
    notes = Column(Text)
    price = Column(Float)  # Price in KES
    vendor = Column(String)  # Where to buy
    image_url = Column(String)  # Product image
    brand = Column(String)  # Brand name
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hike = relationship("Hike", back_populates="equipment")

class PlannedHike(Base):
    __tablename__ = "planned_hikes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hike_id = Column(Integer, ForeignKey("hikes.id"), nullable=False)
    planned_date = Column(DateTime, nullable=False)
    status = Column(String, default="planned")  # planned, completed, cancelled
    notes = Column(Text)
    participants = Column(JSON)  # List of participant user IDs
    transport_mode = Column(String, default="self_drive")  # self_drive, carpool, public_transport
    meeting_point = Column(String)  # GPS coordinates or description
    driving_directions = Column(JSON)  # Waypoints for self-drive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    hike = relationship("Hike")
