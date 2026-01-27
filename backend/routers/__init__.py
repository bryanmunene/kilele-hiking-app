from routers.hikes import router as hikes_router
from routers.auth import router as auth_router
from routers.user_activity import router as activity_router

__all__ = ["hikes_router", "auth_router", "activity_router"]
