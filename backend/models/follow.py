from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User who follows
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User being followed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
