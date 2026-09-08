"""Administrator-only configuration status, without credential values."""
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_active_user
from models.user import User
from mpesa_service import mpesa_service
from strava_service import strava_service
from email_service import email_service

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/status")
def integration_status(user: User = Depends(get_current_active_user)):
    if not user.is_admin:
        raise HTTPException(403, "Administrator access required.")
    return {
        "strava": {"configured": strava_service.is_configured, "redirect_uri": strava_service.redirect_uri},
        "mpesa": {"configured": mpesa_service.configured, "environment": mpesa_service.environment},
        "email": {"configured": email_service.configured, "provider": email_service.provider},
    }
