"""
Background scheduler for automatic Strava activity syncing.
Runs every hour to sync activities for users who have enabled auto-sync.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from models.strava import StravaToken
from strava_service import strava_service
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_all_users():
    """Sync activities for all users with auto-sync enabled"""
    db = SessionLocal()
    try:
        # Get all tokens with auto-sync enabled
        tokens = db.query(StravaToken).filter(
            StravaToken.sync_enabled == True
        ).all()
        
        logger.info(f"Starting auto-sync for {len(tokens)} users")
        
        for token in tokens:
            try:
                logger.info(f"Syncing activities for user {token.user_id}")
                
                # Sync last 7 days of activities
                result = strava_service.sync_activities(
                    db=db,
                    user_id=token.user_id,
                    days=7  # Only sync recent activities to avoid rate limits
                )
                
                logger.info(
                    f"User {token.user_id}: Synced {result['synced']} activities, "
                    f"matched {result['matched']} to trails"
                )
                
            except Exception as e:
                logger.error(f"Failed to sync user {token.user_id}: {str(e)}")
                continue
        
        logger.info("Auto-sync completed")
        
    except Exception as e:
        logger.error(f"Auto-sync failed: {str(e)}")
    finally:
        db.close()

# Initialize scheduler
scheduler = BackgroundScheduler()

def start_scheduler():
    """Start the background scheduler"""
    # Add job to run every hour
    scheduler.add_job(
        func=sync_all_users,
        trigger=IntervalTrigger(hours=1),
        id='strava_auto_sync',
        name='Sync Strava activities for all users',
        replace_existing=True
    )
    
    # Also run once at startup (after 1 minute delay to allow app initialization)
    scheduler.add_job(
        func=sync_all_users,
        trigger='date',
        run_date=datetime.now().replace(second=0, microsecond=0),
        id='strava_initial_sync',
        name='Initial Strava sync on startup'
    )
    
    scheduler.start()
    logger.info("Strava auto-sync scheduler started (runs every hour)")

def stop_scheduler():
    """Stop the scheduler (for graceful shutdown)"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Strava scheduler stopped")
