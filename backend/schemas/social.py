from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Review Schemas
class ReviewCreate(BaseModel):
    hike_id: int
    rating: float = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = None
    difficulty_rating: Optional[str] = None
    conditions: Optional[str] = None
    visited_date: Optional[datetime] = None

class ReviewPhotoResponse(BaseModel):
    id: int
    photo_url: str
    caption: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    hike_id: int
    user_id: int
    rating: float
    title: Optional[str]
    comment: Optional[str]
    difficulty_rating: Optional[str]
    conditions: Optional[str]
    visited_date: Optional[datetime]
    helpful_count: int
    created_at: datetime
    username: Optional[str] = None
    user_profile_picture: Optional[str] = None
    photos: List[ReviewPhotoResponse] = []

    class Config:
        from_attributes = True

# Bookmark Schemas
class BookmarkCreate(BaseModel):
    hike_id: int
    notes: Optional[str] = Field(None, max_length=500)

class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    hike_id: int
    notes: Optional[str]
    created_at: datetime
    hike_name: Optional[str] = None
    hike_location: Optional[str] = None
    hike_image: Optional[str] = None

    class Config:
        from_attributes = True

# Follow Schemas
class FollowCreate(BaseModel):
    following_id: int

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime
    username: Optional[str] = None
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True

# Achievement Schemas
class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    category: Optional[str]
    requirement: Optional[int]
    points: int
    earned: bool = False
    progress: int = 0
    earned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Activity Schemas
class ActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_type: str
    hike_id: Optional[int]
    related_id: Optional[int]
    description: Optional[str]
    created_at: datetime
    username: Optional[str] = None
    user_profile_picture: Optional[str] = None
    hike_name: Optional[str] = None

    class Config:
        from_attributes = True

# Statistics Schemas
class UserStatistics(BaseModel):
    total_hikes: int
    total_distance_km: float
    total_elevation_m: float
    total_duration_hours: float
    total_reviews: int
    average_rating_given: float
    achievements_earned: int
    followers_count: int
    following_count: int
    bookmarks_count: int
