from pydantic import BaseModel, ConfigDict, Field
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
    duration_hours: Optional[float] = None
    elevation_gain_m: Optional[float] = None
    route_data: Optional[str] = None
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None
    status: Optional[str] = None

class HikeSessionResponse(HikeSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    ended_at: Optional[datetime]
    is_active: bool
    status: str
    duration_hours: Optional[float] = 0.0
    elevation_gain_m: Optional[float] = 0.0
    route_data: Optional[str] = None

class SavedHikeCreate(BaseModel):
    hike_id: int

class SavedHikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    hike_id: int
    saved_at: datetime
