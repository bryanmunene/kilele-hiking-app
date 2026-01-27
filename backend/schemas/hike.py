from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class HikeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    difficulty: str = Field(..., pattern="^(Easy|Moderate|Hard|Extreme)$")
    distance_km: float = Field(..., gt=0)
    elevation_gain_m: Optional[float] = Field(None, ge=0)
    estimated_duration_hours: float = Field(..., gt=0)
    description: Optional[str] = None
    trail_type: Optional[str] = Field(None, max_length=100)
    best_season: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    image_url: Optional[str] = Field(None, max_length=500)

class HikeCreate(HikeBase):
    pass

class HikeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    difficulty: Optional[str] = Field(None, pattern="^(Easy|Moderate|Hard|Extreme)$")
    distance_km: Optional[float] = Field(None, gt=0)
    elevation_gain_m: Optional[float] = Field(None, ge=0)
    estimated_duration_hours: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    trail_type: Optional[str] = Field(None, max_length=100)
    best_season: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    image_url: Optional[str] = Field(None, max_length=500)

class HikeResponse(HikeBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
