from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

# Load environment variables first
load_dotenv()

# Initialize Sentry error tracking (if configured)
try:
    import sentry_config
except Exception:
    pass

from database import engine, Base, init_database
from routers import hikes, auth, user_activity, social, messaging, wearable, strava
from config import settings
from rate_limiter import RateLimitExceeded, limiter, rate_limit_handler

# Set up logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
try:
    init_database()
    logger.info("✅ Database initialized")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and stop optional background services with the API."""
    logger.info(f"🚀 Kilele API starting...")
    logger.info(f"📦 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🗄️  Database: {'PostgreSQL' if settings.use_postgresql else 'SQLite'}")
    logger.info(f"☁️  Cloudinary: {'✅ Enabled' if settings.has_cloudinary else '❌ Disabled'}")
    logger.info(f"📧 Email: {'✅ Enabled' if settings.has_email else '❌ Disabled'}")
    logger.info(f"🔍 Sentry: {'✅ Enabled' if settings.has_sentry else '❌ Disabled'}")

    try:
        from strava_scheduler import start_scheduler
        start_scheduler()
        logger.info("🟠 Strava auto-sync scheduler started")
    except Exception as e:
        logger.warning(f"⚠️ Strava scheduler not started: {e}")

    try:
        yield
    finally:
        try:
            from strava_scheduler import stop_scheduler
            stop_scheduler()
            logger.info("🟠 Strava scheduler stopped")
        except Exception:
            pass

# Create FastAPI app
app = FastAPI(
    title="Kilele Hiking API",
    description="API for Kenyan hiking trails and adventures",
    version="2.0.0",
    debug=settings.DEBUG,
    docs_url="/docs" if not settings.is_production else None,  # Hide docs in production
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Include routers
app.include_router(hikes.router, prefix="/api/v1/hikes", tags=["hikes"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(user_activity.router, prefix="/api/v1/user", tags=["user-activity"])
app.include_router(social.router, prefix="/api/v1/social", tags=["social"])
app.include_router(messaging.router, tags=["messaging"])
app.include_router(wearable.router, tags=["wearable"])
app.include_router(strava.router, tags=["strava"])

# Mount static files for images
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    logger.warning("⚠️ Static files directory not found: %s", STATIC_DIR)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Kilele Hiking API",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "PostgreSQL" if settings.use_postgresql else "SQLite",
        "docs": "/docs" if not settings.is_production else "disabled in production"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

@app.get("/api/status")
def api_status():
    """API status and feature flags"""
    return {
        "status": "operational",
        "version": "2.0.0",
        "features": {
            "cloudinary": settings.has_cloudinary,
            "email": settings.has_email,
            "sentry": settings.has_sentry,
            "2fa": settings.ENABLE_2FA,
            "wearables": settings.ENABLE_WEARABLES,
            "social": settings.ENABLE_SOCIAL,
            "messaging": settings.ENABLE_MESSAGING,
            "achievements": settings.ENABLE_ACHIEVEMENTS,
        },
        "database": "PostgreSQL" if settings.use_postgresql else "SQLite",
    }

if __name__ == "__main__":
    import uvicorn
    host = settings.API_BASE_URL.split("://")[1].split(":")[0] if "://" in settings.API_BASE_URL else "0.0.0.0"
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
