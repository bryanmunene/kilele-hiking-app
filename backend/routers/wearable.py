from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import json

from database import get_db
from models.user import User
from models.hike_session import HikeSession
from routers.auth import get_current_active_user
from utils.wearable_parser import WearableDataParser

router = APIRouter(prefix="/api/v1/wearable", tags=["wearable"])

@router.post("/import")
async def import_wearable_data(
    file: UploadFile = File(...),
    hike_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import hiking data from wearable device files (GPX, FIT, TCX)
    Supports Garmin, Fitbit, Apple Watch, Strava, and other devices
    """
    from models.hike import Hike
    from kilele_core.activities import save_activity
    try:
        content = await file.read(10 * 1024 * 1024 + 1)
    finally:
        await file.close()
    try:
        result = save_activity(db, User, Hike, HikeSession, WearableDataParser,
                               current_user.id, file.filename or "", content, hike_id)
        db.commit()
        return {**result, "message": "Activity already saved." if result["duplicate"] else "Activity saved.",
                "route_coordinates": result["summary"].get("route_coordinates", [])}
    except ValueError as exc:
        db.rollback()
        raise HTTPException(400, str(exc))
    except Exception:
        db.rollback()
        raise HTTPException(500, "The activity could not be saved. Please try again.")


@router.get("/sessions/{session_id}/route")
def get_session_route(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get route coordinates for a specific hike session"""
    session = db.query(HikeSession).filter(
        HikeSession.id == session_id,
        HikeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.route_data:
        raise HTTPException(status_code=404, detail="No route data available for this session")
    
    try:
        route_coordinates = json.loads(session.route_data)
        return {
            "session_id": session.id,
            "hike_id": session.hike_id,
            "route_coordinates": route_coordinates,
            "total_points": len(route_coordinates)
        }
    except:
        raise HTTPException(status_code=500, detail="Failed to parse route data")

@router.get("/supported-devices")
def get_supported_devices():
    """Get list of supported wearable devices and file formats"""
    return {
        "supported_devices": [
            {
                "name": "Garmin Watches",
                "models": ["Forerunner, Fenix, Instinct, vivoactive, Epix, etc."],
                "formats": ["GPX", "FIT"],
                "export_method": "Garmin Connect: Open activity → ⚙️ Settings → Export Original/GPX",
                "tested": True,
                "notes": "FIT is native format, GPX also supported"
            },
            {
                "name": "Apple Watch",
                "models": ["Series 2+ with GPS"],
                "formats": ["GPX"],
                "export_method": "Use HealthFit or similar app to export workouts as GPX",
                "tested": True,
                "notes": "Requires third-party app (HealthFit, RunGap, WorkOutDoors)"
            },
            {
                "name": "Strava",
                "models": ["Any device synced to Strava"],
                "formats": ["GPX", "TCX"],
                "export_method": "Open activity → ⋯ Menu → Export GPX",
                "tested": True,
                "notes": "Works with any GPS device that syncs to Strava"
            },
            {
                "name": "Fitbit",
                "models": ["Versa, Sense, Charge 5+, Ionic"],
                "formats": ["GPX", "TCX"],
                "export_method": "Sync to Strava, then export from Strava",
                "tested": True,
                "notes": "Fitbit doesn't export directly - use Strava or third-party tools"
            },
            {
                "name": "Samsung Galaxy Watch",
                "models": ["Galaxy Watch 4+, Active 2"],
                "formats": ["GPX"],
                "export_method": "Samsung Health → Workout → Share → Export as GPX",
                "tested": False,
                "notes": "May require Samsung Health Web interface"
            },
            {
                "name": "Suunto",
                "models": ["Suunto 9, 7, 5, Spartan"],
                "formats": ["GPX", "FIT"],
                "export_method": "Suunto app → Activity → Export → GPX/FIT",
                "tested": False,
                "notes": "Suunto native formats fully supported"
            },
            {
                "name": "Polar",
                "models": ["Vantage, Grit X, Pacer, Ignite"],
                "formats": ["GPX", "TCX"],
                "export_method": "Polar Flow web → Training → Export → TCX/GPX",
                "tested": False,
                "notes": "Export from website, not mobile app"
            },
            {
                "name": "Coros",
                "models": ["Pace, Apex, Vertix"],
                "formats": ["GPX", "FIT"],
                "export_method": "Coros app → Workout → Export",
                "tested": False,
                "notes": "Multi-sport GPS watches"
            }
        ],
        "file_formats": {
            "GPX": "GPS Exchange Format - Universal standard, works with all devices",
            "FIT": "Flexible and Interoperable Data Transfer - Garmin's native format, most detailed",
            "TCX": "Training Center XML - Compatible with many fitness platforms"
        },
        "tips": [
            "GPX format is most widely supported and recommended",
            "Make sure GPS was enabled during your hike",
            "Larger files (more GPS points) = more accurate route",
            "Export 'Original' or 'Full' data when available"
        ]
    }
