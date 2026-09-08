"""
Strava OAuth and API integration service
Handles authentication, activity sync, and webhook events
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
import os
import requests
try:
    from stravalib import Client
except ImportError:
    Client = None
from sqlalchemy.orm import Session
from models.strava import StravaToken, StravaActivity
from models.hike_session import HikeSession
from models.hike import Hike
import json
from config import settings

class StravaService:
    """Service for Strava API integration"""
    
    def __init__(self):
        self.client_id = os.getenv("STRAVA_CLIENT_ID")
        self.client_secret = os.getenv("STRAVA_CLIENT_SECRET")
        self.redirect_uri = os.getenv("STRAVA_REDIRECT_URI") or settings.FRONTEND_URL + "/Strava"
        self.is_available = Client is not None
        self.is_configured = self.is_available and bool(self.client_id and self.client_secret)
        
        if not self.is_available:
            print("WARNING: stravalib is not installed - Strava integration disabled")
        if not self.is_configured:
            print("WARNING: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET not set - Strava integration disabled")

    def _client(self, **kwargs):
        if Client is None:
            raise ValueError("Strava integration package is not installed. Install backend requirements to enable Strava.")
        return Client(**kwargs)
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate OAuth authorization URL"""
        if not self.is_configured:
            raise ValueError("Strava API credentials not configured. Please set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET environment variables.")
        
        client = self._client()
        url = client.authorization_url(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=['read', 'activity:read'],
            state=state
        )
        return url
    
    def exchange_code_for_token(self, code: str, db: Session, user_id: int, scope: str = "") -> StravaToken:
        """Exchange authorization code for access token"""
        client = self._client()
        
        # Exchange code for token
        token_response = client.exchange_code_for_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code
        )
        granted = token_response.get('scope', scope)
        granted = granted.replace(' ', ',') if isinstance(granted, str) else ','.join(granted)
        if not {'activity:read', 'activity:read_all'}.intersection(granted.split(',')):
            raise ValueError("Activity access was not granted. Reconnect and allow activity access.")
        athlete_id = token_response.get('athlete', {}).get('id')
        if athlete_id is None:
            athlete_id = self._client(access_token=token_response['access_token']).get_athlete().id
        other = db.query(StravaToken).filter(StravaToken.athlete_id == athlete_id, StravaToken.user_id != user_id).first()
        if other:
            raise ValueError("This Strava account is already connected to another Kilele account.")
        
        # Check if user already has a token
        existing_token = db.query(StravaToken).filter(StravaToken.user_id == user_id).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = token_response['access_token']
            existing_token.refresh_token = token_response['refresh_token']
            existing_token.expires_at = datetime.fromtimestamp(token_response['expires_at'], timezone.utc).replace(tzinfo=None)
            existing_token.athlete_id = athlete_id
            existing_token.scope = granted
            existing_token.connected_at = datetime.utcnow()
            existing_token.sync_enabled = True
            db.commit()
            return existing_token
        
        # Create new token
        token = StravaToken(
            user_id=user_id,
            access_token=token_response['access_token'],
            refresh_token=token_response['refresh_token'],
            expires_at=datetime.fromtimestamp(token_response['expires_at'], timezone.utc).replace(tzinfo=None),
            athlete_id=athlete_id,
            scope=granted
        )
        
        db.add(token)
        db.commit()
        db.refresh(token)
        
        return token
    
    def refresh_access_token(self, token: StravaToken, db: Session) -> StravaToken:
        """Refresh expired access token"""
        client = self._client()
        
        refresh_response = client.refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=token.refresh_token
        )
        
        token.access_token = refresh_response['access_token']
        token.refresh_token = refresh_response['refresh_token']
        token.expires_at = datetime.fromtimestamp(refresh_response['expires_at'], timezone.utc).replace(tzinfo=None)
        
        db.commit()
        return token
    
    def get_valid_token(self, user_id: int, db: Session) -> Optional[StravaToken]:
        """Get valid access token, refreshing if necessary"""
        token = db.query(StravaToken).filter(StravaToken.user_id == user_id).first()
        
        if not token:
            return None
        
        # Check if token is expired (with 5 minute buffer)
        if token.expires_at < datetime.utcnow() + timedelta(minutes=5):
            token = self.refresh_access_token(token, db)
        
        return token
    
    def sync_activities(self, user_id: int, db: Session, after: datetime = None, limit: int = 100) -> List[StravaActivity]:
        """Sync activities from Strava"""
        token = self.get_valid_token(user_id, db)
        
        if not token:
            raise ValueError("User not connected to Strava")
        
        client = self._client(access_token=token.access_token)
        
        # Default to last 30 days if no after date
        if not after:
            after = datetime.utcnow() - timedelta(days=30)
        
        # Fetch activities
        activities = client.get_activities(after=after, limit=limit)
        
        synced_activities = []
        
        for activity in activities:
            # Only sync hiking/walking activities
            activity_type = getattr(activity, 'sport_type', None) or activity.type
            activity_type = str(getattr(activity_type, 'root', activity_type))
            if activity_type not in ['Hike', 'Walk', 'TrailRun', 'Run']:
                continue
            
            # Check if activity already exists
            existing = db.query(StravaActivity).filter(
                StravaActivity.strava_activity_id == str(activity.id),
                StravaActivity.user_id == user_id
            ).first()
            
            if existing:
                # Update existing activity
                self._update_activity_from_strava(existing, activity, db)
                synced_activities.append(existing)
            else:
                # Create new activity
                new_activity = self._create_activity_from_strava(
                    activity, token.id, user_id, db
                )
                synced_activities.append(new_activity)
        
        # Update last synced time
        token.last_synced = datetime.utcnow()
        db.commit()
        
        return synced_activities
    
    def _create_activity_from_strava(
        self, 
        strava_activity, 
        token_id: int, 
        user_id: int, 
        db: Session
    ) -> StravaActivity:
        """Create StravaActivity from Strava API data"""
        
        def seconds(value):
            return int(value.total_seconds() if hasattr(value, 'total_seconds') else value or 0)

        def coordinates(value):
            value = getattr(value, 'root', value)
            return json.dumps(list(value)) if value else None

        activity = StravaActivity(
            token_id=token_id,
            user_id=user_id,
            strava_activity_id=str(strava_activity.id),
            name=strava_activity.name,
            activity_type=str(getattr(strava_activity.type, 'root', strava_activity.type)),
            distance=float(strava_activity.distance) if strava_activity.distance else None,
            moving_time=seconds(strava_activity.moving_time),
            elapsed_time=seconds(strava_activity.elapsed_time),
            total_elevation_gain=float(strava_activity.total_elevation_gain) if strava_activity.total_elevation_gain else None,
            start_date=strava_activity.start_date,
            start_date_local=strava_activity.start_date_local,
            start_latlng=coordinates(strava_activity.start_latlng),
            end_latlng=coordinates(strava_activity.end_latlng),
            map_summary_polyline=strava_activity.map.summary_polyline if strava_activity.map else None,
            average_speed=float(strava_activity.average_speed) if strava_activity.average_speed else None,
            max_speed=float(strava_activity.max_speed) if strava_activity.max_speed else None,
            average_heartrate=float(strava_activity.average_heartrate) if strava_activity.average_heartrate else None,
            max_heartrate=float(strava_activity.max_heartrate) if strava_activity.max_heartrate else None,
            calories=float(getattr(strava_activity, 'calories', 0) or 0),
            achievement_count=int(strava_activity.achievement_count) if strava_activity.achievement_count else 0,
            kudos_count=int(strava_activity.kudos_count) if strava_activity.kudos_count else 0,
            comment_count=int(strava_activity.comment_count) if strava_activity.comment_count else 0,
            photo_count=int(strava_activity.total_photo_count) if strava_activity.total_photo_count else 0
        )
        
        db.add(activity)
        db.commit()
        db.refresh(activity)
        
        # Try to match activity to existing trail
        self._match_activity_to_trail(activity, db)
        
        return activity
    
    def _update_activity_from_strava(
        self, 
        activity: StravaActivity, 
        strava_activity, 
        db: Session
    ):
        """Update existing activity with latest Strava data"""
        activity.name = strava_activity.name
        activity.kudos_count = int(strava_activity.kudos_count) if strava_activity.kudos_count else 0
        activity.comment_count = int(strava_activity.comment_count) if strava_activity.comment_count else 0
        activity.updated_at = datetime.utcnow()
        
        db.commit()
    
    def _match_activity_to_trail(self, activity: StravaActivity, db: Session):
        """Try to match Strava activity to a trail in our database"""
        if not activity.start_latlng:
            return
        
        try:
            start_coords = json.loads(activity.start_latlng)
            if len(start_coords) != 2:
                return
            
            lat, lng = start_coords
            
            # Find trails within ~5km radius
            trails = db.query(Hike).filter(
                Hike.latitude.between(lat - 0.05, lat + 0.05),
                Hike.longitude.between(lng - 0.05, lng + 0.05)
            ).all()
            
            if len(trails) == 1:
                # Only one trail nearby, likely a match
                activity.is_matched_to_trail = True
                activity.matched_hike_id = trails[0].id
                db.commit()
        
        except Exception as e:
            print(f"Error matching activity to trail: {e}")
    
    def disconnect_strava(self, user_id: int, db: Session) -> bool:
        """Disconnect Strava account"""
        token = db.query(StravaToken).filter(StravaToken.user_id == user_id).first()
        
        if not token:
            return False
        
        # Revoke token with Strava
        response = requests.post(
            "https://www.strava.com/oauth/revoke",
            auth=(self.client_id, self.client_secret),
            data={"token": token.refresh_token, "token_type_hint": "refresh_token"},
            timeout=20,
        )
        response.raise_for_status()
        
        # Delete token and activities
        db.delete(token)
        db.commit()
        
        return True
    
    def get_user_stats(self, user_id: int, db: Session) -> Dict:
        """Get user's Strava activity statistics"""
        activities = db.query(StravaActivity).filter(
            StravaActivity.user_id == user_id
        ).all()
        
        total_distance = sum(a.distance or 0 for a in activities) / 1000  # km
        total_time = sum(a.moving_time or 0 for a in activities) / 3600  # hours
        total_elevation = sum(a.total_elevation_gain or 0 for a in activities)
        total_kudos = sum(a.kudos_count or 0 for a in activities)
        
        return {
            "total_activities": len(activities),
            "total_distance_km": round(total_distance, 2),
            "total_time_hours": round(total_time, 2),
            "total_elevation_m": round(total_elevation, 2),
            "total_kudos": total_kudos,
            "matched_trails": sum(1 for a in activities if a.is_matched_to_trail)
        }


# Singleton instance
strava_service = StravaService()
