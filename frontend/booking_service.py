"""Thin database adapters for shared booking logic."""
import models
from database import get_db
from kilele_core import bookings


def upcoming_events(trail_id=None, event_id=None):
    with get_db() as db:
        return bookings.upcoming_events(db, models, trail_id, event_id)


def register_free(user_id, event_id, phone_number=""):
    try:
        with get_db() as db:
            return bookings.register_free(db, models, user_id, event_id, phone_number)
    except bookings.BookingError as exc:
        return {"error": str(exc)}


def cancel(user_id, registration_id):
    try:
        with get_db() as db:
            return bookings.cancel(db, models, user_id, registration_id)
    except bookings.BookingError as exc:
        return {"error": str(exc)}


def registrations_for(user_id):
    with get_db() as db:
        return bookings.registrations_for(db, models, user_id)
