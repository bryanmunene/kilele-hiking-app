from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models.user import User
from models.hike import Hike
from models.hike_session import HikeSession, SavedHike
from schemas.hike_session import (
    HikeSessionCreate, HikeSessionUpdate, HikeSessionResponse,
    SavedHikeCreate, SavedHikeResponse
)
from auth import get_current_active_user

router = APIRouter()

# Hike Session Endpoints
@router.post("/sessions", response_model=HikeSessionResponse, status_code=201)
def start_hike_session(
    session: HikeSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start a new hike session"""
    # Check if hike exists
    hike = db.query(Hike).filter(Hike.id == session.hike_id).first()
    if not hike:
        raise HTTPException(status_code=404, detail="Hike not found")
    
    # Check if user already has an active session for this hike
    existing_session = db.query(HikeSession).filter(
        HikeSession.user_id == current_user.id,
        HikeSession.hike_id == session.hike_id,
        HikeSession.is_active == True
    ).first()
    
    if existing_session:
        raise HTTPException(status_code=400, detail="You already have an active session for this hike")
    
    # Create new session
    db_session = HikeSession(
        user_id=current_user.id,
        hike_id=session.hike_id
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.get("/sessions", response_model=List[HikeSessionResponse])
def get_user_sessions(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all hike sessions for current user"""
    query = db.query(HikeSession).filter(HikeSession.user_id == current_user.id)
    
    if active_only:
        query = query.filter(HikeSession.is_active == True)
    
    sessions = query.order_by(HikeSession.started_at.desc()).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=HikeSessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific hike session"""
    session = db.query(HikeSession).filter(
        HikeSession.id == session_id,
        HikeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@router.put("/sessions/{session_id}", response_model=HikeSessionResponse)
def update_session(
    session_id: int,
    session_update: HikeSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update hike session (track progress, complete hike)"""
    db_session = db.query(HikeSession).filter(
        HikeSession.id == session_id,
        HikeSession.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update fields
    update_data = session_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_session, key, value)
    
    # If marking as inactive (completed), set completed timestamp
    if update_data.get('is_active') == False and db_session.is_active:
        db_session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a hike session"""
    db_session = db.query(HikeSession).filter(
        HikeSession.id == session_id,
        HikeSession.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    return None

# Saved Hikes Endpoints
@router.post("/saved", response_model=SavedHikeResponse, status_code=201)
def save_hike(
    saved_hike: SavedHikeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Save a hike to favorites"""
    # Check if hike exists
    hike = db.query(Hike).filter(Hike.id == saved_hike.hike_id).first()
    if not hike:
        raise HTTPException(status_code=404, detail="Hike not found")
    
    # Check if already saved
    existing = db.query(SavedHike).filter(
        SavedHike.user_id == current_user.id,
        SavedHike.hike_id == saved_hike.hike_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Hike already saved")
    
    # Create saved hike
    db_saved = SavedHike(
        user_id=current_user.id,
        hike_id=saved_hike.hike_id
    )
    
    db.add(db_saved)
    db.commit()
    db.refresh(db_saved)
    
    return db_saved

@router.get("/saved", response_model=List[SavedHikeResponse])
def get_saved_hikes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all saved hikes for current user"""
    saved = db.query(SavedHike).filter(
        SavedHike.user_id == current_user.id
    ).order_by(SavedHike.saved_at.desc()).all()
    
    return saved

@router.delete("/saved/{hike_id}", status_code=204)
def unsave_hike(
    hike_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a hike from favorites"""
    saved = db.query(SavedHike).filter(
        SavedHike.user_id == current_user.id,
        SavedHike.hike_id == hike_id
    ).first()
    
    if not saved:
        raise HTTPException(status_code=404, detail="Saved hike not found")
    
    db.delete(saved)
    db.commit()
    return None

# Statistics Endpoints
@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user hiking statistics"""
    # Total sessions
    total_sessions = db.query(HikeSession).filter(
        HikeSession.user_id == current_user.id
    ).count()
    
    # Completed hikes
    completed = db.query(HikeSession).filter(
        HikeSession.user_id == current_user.id,
        HikeSession.is_active == False
    ).count()
    
    # Active hikes
    active = db.query(HikeSession).filter(
        HikeSession.user_id == current_user.id,
        HikeSession.is_active == True
    ).count()
    
    # Total distance
    total_distance = db.query(HikeSession).filter(
        HikeSession.user_id == current_user.id
    ).with_entities(
        db.func.sum(HikeSession.distance_covered_km)
    ).scalar() or 0
    
    # Total duration
    total_duration = db.query(HikeSession).filter(
        HikeSession.user_id == current_user.id
    ).with_entities(
        db.func.sum(HikeSession.duration_minutes)
    ).scalar() or 0
    
    # Saved hikes count
    saved_count = db.query(SavedHike).filter(
        SavedHike.user_id == current_user.id
    ).count()
    
    return {
        "total_sessions": total_sessions,
        "completed_hikes": completed,
        "active_hikes": active,
        "total_distance_km": float(total_distance),
        "total_duration_hours": round(total_duration / 60, 2),
        "saved_hikes_count": saved_count
    }
