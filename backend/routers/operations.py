"""Organizer-only operational controls."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from auth import get_current_admin
from database import get_db
from email_service import email_service
from kilele_core.operations import outbox
from kilele_core.security import throttle, TooManyAttempts
from notification_worker import deliver_pending

router = APIRouter(prefix="/api/v1/admin", tags=["operations"])


@router.post("/notifications/retry")
def retry_notifications(user=Depends(get_current_admin), db: Session = Depends(get_db)):
    if not email_service.configured:
        raise HTTPException(503, "Email delivery needs provider authorization before messages can be sent.")
    try:
        throttle(db, "retry-mail", str(user.id), limit=3)
    except TooManyAttempts as exc:
        raise HTTPException(429, str(exc))
    db.execute(update(outbox).where(outbox.c.sent_at.is_(None), outbox.c.attempts >= 8,
        outbox.c.available_at <= datetime.utcnow()).values(attempts=0, available_at=datetime.utcnow()))
    db.commit()
    result = deliver_pending()
    return {"message": f"Sent {result['sent']} queued emails. Other messages keep their retry schedule."}
