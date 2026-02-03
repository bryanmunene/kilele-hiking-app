"""
Strava API routes for OAuth, activity sync, and webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from auth import get_current_user
from strava_service import strava_service
from models.strava import StravaActivity, StravaToken
import os

router = APIRouter(prefix="/api/strava", tags=["strava"])


class StravaConnectResponse(BaseModel):
    authorization_url: str


class StravaCallbackRequest(BaseModel):
    code: str
    state: str = None


class StravaActivityResponse(BaseModel):
    id: int
    name: str
    activity_type: str
    distance_km: float
    duration_minutes: int
    date: str
    kudos_count: int
    is_matched: bool
    matched_trail_name: str = None


class StravaStatsResponse(BaseModel):
    total_activities: int
    total_distance_km: float
    total_time_hours: float
    total_elevation_m: float
    total_kudos: int
    matched_trails: int
    is_connected: bool
    last_synced: str = None


@router.get("/connect", response_model=StravaConnectResponse)
async def connect_strava(current_user: dict = Depends(get_current_user)):
    """
    Get Strava OAuth authorization URL
    """
    try:
        if not strava_service.is_configured:
            raise HTTPException(
                status_code=503,
                detail="Strava integration is not configured. Please contact administrator to set up Strava API credentials."
            )
        
        state = f"user_{current_user['id']}"
        auth_url = strava_service.get_authorization_url(state=state)
        
        return {"authorization_url": auth_url}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate authorization URL: {str(e)}")


@router.post("/callback")
async def strava_callback(
    request: StravaCallbackRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Handle OAuth callback from Strava
    """
    try:
        token = strava_service.exchange_code_for_token(
            code=request.code,
            db=db,
            user_id=current_user['id']
        )
        
        return {
            "success": True,
            "message": "Successfully connected to Strava",
            "athlete_id": token.athlete_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sync")
async def sync_activities(
    background_tasks: BackgroundTasks,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Sync activities from Strava
    """
    try:
        # Check if user is connected
        token = db.query(StravaToken).filter(StravaToken.user_id == current_user['id']).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Strava not connected")
        
        # Sync activities in background
        after_date = datetime.utcnow() - timedelta(days=days)
        
        activities = strava_service.sync_activities(
            user_id=current_user['id'],
            db=db,
            after=after_date
        )
        
        return {
            "success": True,
            "synced_count": len(activities),
            "message": f"Synced {len(activities)} activities from the last {days} days"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/activities", response_model=List[StravaActivityResponse])
async def get_activities(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's synced Strava activities
    """
    activities = db.query(StravaActivity).filter(
        StravaActivity.user_id == current_user['id']
    ).order_by(StravaActivity.start_date.desc()).limit(limit).all()
    
    result = []
    for activity in activities:
        result.append({
            "id": activity.id,
            "name": activity.name,
            "activity_type": activity.activity_type,
            "distance_km": round(activity.distance / 1000, 2) if activity.distance else 0,
            "duration_minutes": round(activity.moving_time / 60, 0) if activity.moving_time else 0,
            "date": activity.start_date_local.isoformat() if activity.start_date_local else activity.start_date.isoformat(),
            "kudos_count": activity.kudos_count or 0,
            "is_matched": activity.is_matched_to_trail,
            "matched_trail_name": activity.matched_hike.name if activity.matched_hike else None
        })
    
    return result


@router.get("/stats", response_model=StravaStatsResponse)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's Strava statistics
    """
    token = db.query(StravaToken).filter(StravaToken.user_id == current_user['id']).first()
    
    if not token:
        return {
            "total_activities": 0,
            "total_distance_km": 0,
            "total_time_hours": 0,
            "total_elevation_m": 0,
            "total_kudos": 0,
            "matched_trails": 0,
            "is_connected": False
        }
    
    stats = strava_service.get_user_stats(current_user['id'], db)
    stats['is_connected'] = True
    stats['last_synced'] = token.last_synced.isoformat() if token.last_synced else None
    
    return stats


@router.delete("/disconnect")
async def disconnect_strava(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Disconnect Strava account
    """
    success = strava_service.disconnect_strava(current_user['id'], db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Strava not connected")
    
    return {
        "success": True,
        "message": "Strava account disconnected successfully"
    }


# Webhook endpoints
WEBHOOK_VERIFY_TOKEN = os.getenv("STRAVA_WEBHOOK_VERIFY_TOKEN", "kilele_hiking_app_2026")


@router.get("/webhook")
async def webhook_verify(request: Request):
    """
    Verify webhook subscription with Strava
    """
    params = dict(request.query_params)
    
    # Strava sends: hub.mode, hub.challenge, hub.verify_token
    if params.get("hub.verify_token") == WEBHOOK_VERIFY_TOKEN:
        return {"hub.challenge": params.get("hub.challenge")}
    
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/webhook")
async def webhook_event(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle webhook events from Strava
    Events: create, update, delete activities
    """
    try:
        data = await request.json()
        
        # Strava webhook event structure:
        # {
        #   "object_type": "activity",
        #   "object_id": 123456,
        #   "aspect_type": "create|update|delete",
        #   "owner_id": 789,  # Strava athlete ID
        #   "subscription_id": 123,
        #   "event_time": 1516126040
        # }
        
        if data.get("object_type") != "activity":
            return {"status": "ignored"}
        
        athlete_id = data.get("owner_id")
        aspect_type = data.get("aspect_type")
        activity_id = data.get("object_id")
        
        # Find user by athlete ID
        token = db.query(StravaToken).filter(StravaToken.athlete_id == athlete_id).first()
        
        if not token or not token.sync_enabled:
            return {"status": "ignored"}
        
        # Handle different event types
        if aspect_type == "create":
            # Sync new activity in background
            background_tasks.add_task(
                strava_service.sync_activities,
                token.user_id,
                db,
                datetime.utcnow() - timedelta(hours=1),
                limit=5
            )
        
        elif aspect_type == "delete":
            # Delete activity from our database
            activity = db.query(StravaActivity).filter(
                StravaActivity.strava_activity_id == str(activity_id)
            ).first()
            
            if activity:
                db.delete(activity)
                db.commit()
        
        elif aspect_type == "update":
            # Re-sync activity
            background_tasks.add_task(
                strava_service.sync_activities,
                token.user_id,
                db,
                datetime.utcnow() - timedelta(hours=1),
                limit=5
            )
        
        return {"status": "processed"}
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/toggle-autosync")
async def toggle_autosync(
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Enable/disable automatic activity syncing
    """
    token = db.query(StravaToken).filter(StravaToken.user_id == current_user['id']).first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Strava not connected")
    
    token.sync_enabled = enabled
    db.commit()
    
    return {
        "success": True,
        "sync_enabled": enabled,
        "message": f"Auto-sync {'enabled' if enabled else 'disabled'}"
    }
