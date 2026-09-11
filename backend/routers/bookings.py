"""Public group-hike discovery and authenticated, idempotent free bookings."""
from types import SimpleNamespace
from fastapi import APIRouter, Depends, HTTPException, Request
from auth import get_current_active_user
from database import get_db
from models.booking import HikeRegistration, Payment, PlannedHike
from models.hike import Hike
from models.user import User
from kilele_core import bookings
from rate_limiter import limiter

models = SimpleNamespace(HikeRegistration=HikeRegistration, Payment=Payment,
                         PlannedHike=PlannedHike, Hike=Hike, User=User)
router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])


@router.get("/events")
def events(trail_id: int | None = None, db=Depends(get_db)):
    return bookings.upcoming_events(db, models, trail_id)


@router.get("/mine")
def mine(user=Depends(get_current_active_user), db=Depends(get_db)):
    return bookings.registrations_for(db, models, user.id)


@router.post("/events/{event_id}/register")
@limiter.limit("10/minute")
def register(request: Request, event_id: int, user=Depends(get_current_active_user), db=Depends(get_db)):
    try:
        result = bookings.register_free(db, models, user.id, event_id)
        db.commit()
        return result
    except bookings.BookingError as exc:
        raise HTTPException(409, str(exc)) from None


@router.post("/{registration_id}/cancel")
@limiter.limit("10/minute")
def cancel(request: Request, registration_id: int, user=Depends(get_current_active_user), db=Depends(get_db)):
    try:
        result = bookings.cancel(db, models, user.id, registration_id)
        db.commit()
        return result
    except bookings.BookingError as exc:
        raise HTTPException(409, str(exc)) from None
