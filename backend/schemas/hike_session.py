from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class HikeSessionBase(BaseModel):
    hike_id: int
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    distance_covered_km: Optional[float] = 0.0
    duration_minutes: Optional[int] = 0
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

class HikeSessionCreate(BaseModel):
    hike_id: int

class HikeSessionUpdate(BaseModel):
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    distance_covered_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None

class HikeSessionResponse(HikeSessionBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class SavedHikeCreate(BaseModel):
    hike_id: int

class SavedHikeResponse(BaseModel):
    id: int
    user_id: int
    hike_id: int
    saved_at: datetime

    class Config:
        from_attributes = True
