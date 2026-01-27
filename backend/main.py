from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from database import engine, Base
from routers import hikes, auth, user_activity, social, messaging, wearable

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kilele Hiking API",
    description="API for Kenyan hiking trails and adventures",
    version="1.0.0"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hikes.router, prefix="/api/v1/hikes", tags=["hikes"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(user_activity.router, prefix="/api/v1/user", tags=["user-activity"])
app.include_router(social.router, prefix="/api/v1/social", tags=["social"])
app.include_router(messaging.router, tags=["messaging"])
app.include_router(wearable.router, tags=["wearable"])

# Mount static files for images
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Kilele Hiking API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
