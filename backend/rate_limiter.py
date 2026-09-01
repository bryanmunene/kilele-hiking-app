"""
Rate limiting middleware for Kilele backend
Prevents abuse and DDoS attacks
"""
from fastapi import Request
from fastapi.responses import JSONResponse

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
except ImportError:
    class RateLimitExceeded(Exception):
        """Fallback exception used when slowapi is not installed."""
        detail = "Rate limiting is unavailable"

    def get_remote_address(request: Request) -> str:
        client = getattr(request, "client", None)
        return client.host if client else "local"

    class Limiter:
        """No-op limiter so the API can run without optional slowapi."""
        def __init__(self, *args, **kwargs):
            pass

        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

try:
    from config import settings
    RATE_LIMIT_LOGIN = settings.RATE_LIMIT_LOGIN
    RATE_LIMIT_API = settings.RATE_LIMIT_API
    RATE_LIMIT_UPLOAD = settings.RATE_LIMIT_UPLOAD
except Exception:
    RATE_LIMIT_LOGIN = 5
    RATE_LIMIT_API = 60
    RATE_LIMIT_UPLOAD = 10

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Custom rate limit error handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "message": "You have exceeded the rate limit. Please try again later.",
            "retry_after": exc.detail
        }
    )

# Rate limit decorators for different endpoints
def rate_limit_login():
    """Rate limit for login endpoints (5 requests/minute)"""
    return limiter.limit(f"{RATE_LIMIT_LOGIN}/minute")

def rate_limit_api():
    """Rate limit for general API endpoints (60 requests/minute)"""
    return limiter.limit(f"{RATE_LIMIT_API}/minute")

def rate_limit_upload():
    """Rate limit for file uploads (10 requests/minute)"""
    return limiter.limit(f"{RATE_LIMIT_UPLOAD}/minute")
