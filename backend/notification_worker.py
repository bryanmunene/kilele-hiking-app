"""Retryable outbox delivery. A mail outage never rolls back a booking."""
from datetime import datetime, timedelta
from sqlalchemy import select, update
from database import get_db_context
from email_service import email_service
from kilele_core.operations import outbox
from models.user import User


def deliver_pending(limit=10):
    if not email_service.configured:
        return {"sent": 0, "available": False}
    sent = 0
    for _ in range(min(limit, 20)):
        with get_db_context() as db:
            row = db.execute(select(outbox).where(outbox.c.sent_at.is_(None),
                outbox.c.available_at <= datetime.utcnow(), outbox.c.attempts < 8)
                .order_by(outbox.c.created_at).with_for_update(skip_locked=True).limit(1)).mappings().first()
            if row is None:
                break
            item = dict(row)
            db.execute(update(outbox).where(outbox.c.key == item["key"]).values(
                attempts=item["attempts"] + 1, available_at=datetime.utcnow() + timedelta(minutes=10)))
            user = db.get(User, item["user_id"])
            recipient = (user.email, user.username) if user and user.is_active else None
        delivered = False
        if recipient:
            email, username = recipient
            payload = item["payload"]
            if item["kind"] == "welcome":
                delivered = email_service.send_welcome_email(email, username)
            elif item["kind"] == "booking":
                delivered = email_service.send_booking_confirmation(email, payload["hike"], str(payload["reference"]))
            elif item["kind"] == "cancellation":
                delivered = email_service.send_booking_cancellation(email, payload["hike"], str(payload["reference"]))
        with get_db_context() as db:
            db.execute(update(outbox).where(outbox.c.key == item["key"]).values(
                sent_at=datetime.utcnow() if delivered or not recipient else None,
                available_at=datetime.utcnow() + timedelta(minutes=min(24 * 60, 2 ** (item["attempts"] + 1)))))
        sent += int(delivered)
    return {"sent": sent, "available": True}
