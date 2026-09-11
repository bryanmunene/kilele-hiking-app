"""Booking contracts shared by the website and API; callers own transactions."""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import func
from .operations import enqueue


class BookingError(ValueError):
    pass


def active_member(db, models, user_id):
    user = db.get(models.User, user_id)
    if not user or not user.is_active:
        raise BookingError("Sign in with an active account to continue.")
    return user


def lock_open_hike(db, models, planned_hike_id):
    hike = db.query(models.PlannedHike).filter_by(id=planned_hike_id).with_for_update().first()
    if not hike or hike.status != "planned" or hike.planned_date <= datetime.utcnow():
        raise BookingError("This hike is no longer open for registration.")
    organizer = db.get(models.User, hike.user_id)
    if not organizer or not organizer.is_active or not organizer.is_admin:
        raise BookingError("This hike is not open for public registration.")
    return hike


def ensure_capacity(db, models, hike, registration=None):
    if registration and registration.status != "cancelled":
        return
    count = db.query(models.HikeRegistration).filter(
        models.HikeRegistration.planned_hike_id == hike.id,
        models.HikeRegistration.status != "cancelled").count()
    if hike.max_participants and count >= hike.max_participants:
        raise BookingError("This hike is full.")


def register_free(db, models, user_id, planned_hike_id, phone_number=""):
    active_member(db, models, user_id)
    hike = lock_open_hike(db, models, planned_hike_id)
    if (hike.price or 0) > 0:
        raise BookingError("Paid registrations must use the secure checkout service.")
    registration = db.query(models.HikeRegistration).filter_by(
        planned_hike_id=hike.id, user_id=user_id).first()
    if registration and registration.status != "cancelled":
        return {"registration_id": registration.id, "status": registration.status,
                "payment_required": False, "amount": 0, "duplicate": True}
    ensure_capacity(db, models, hike, registration)
    registration = registration or models.HikeRegistration(planned_hike_id=hike.id, user_id=user_id)
    registration.status, registration.payment_status = "confirmed", "paid"
    registration.phone_number = phone_number
    db.add(registration)
    db.flush()
    trail = db.get(models.Hike, hike.hike_id)
    enqueue(db, f"booking:{registration.id}:{uuid4().hex}", user_id, "booking",
            {"hike": trail.name, "reference": registration.id})
    return {"registration_id": registration.id, "status": "confirmed", "payment_required": False,
            "amount": 0, "duplicate": False}


def cancel(db, models, user_id, registration_id):
    active_member(db, models, user_id)
    owned = db.query(models.HikeRegistration).filter_by(id=registration_id, user_id=user_id).first()
    if not owned:
        raise BookingError("Registration not found.")
    # Match the hike -> registration lock order used by checkout and organizers.
    hike = db.query(models.PlannedHike).filter_by(id=owned.planned_hike_id).with_for_update().first()
    registration = db.query(models.HikeRegistration).filter_by(id=registration_id, user_id=user_id).populate_existing().with_for_update().one()
    if registration.status == "cancelled":
        return {"message": "Registration already cancelled."}
    if not hike or hike.planned_date <= datetime.utcnow():
        raise BookingError("Contact support about a past hike.")
    if (hike.price or 0) > 0 or db.query(models.Payment).filter_by(registration_id=registration.id).first():
        raise BookingError("Contact kileleexplorers@gmail.com to reconcile payment and request cancellation/refund.")
    registration.status = "cancelled"
    trail = db.get(models.Hike, hike.hike_id)
    enqueue(db, f"cancel:{registration.id}:{uuid4().hex}", user_id, "cancellation",
            {"hike": trail.name, "reference": registration.id})
    db.flush()
    return {"message": "Registration cancelled. Your place has been released."}


def event_details(hike, trail, organizer, count):
    return {"id": hike.id, "hike_id": trail.id, "name": trail.name, "location": trail.location,
            "planned_date": hike.planned_date.isoformat(), "price": hike.price or 0,
            "capacity": hike.max_participants, "count": count,
            "spots": max(0, hike.max_participants - count) if hike.max_participants else None,
            "description": hike.notes or trail.description or "", "difficulty": trail.difficulty,
            "meeting_point": hike.meeting_point, "transport_mode": hike.transport_mode,
            "organizer": (organizer.full_name or organizer.username) if organizer else "Kilele Explorers",
            "image_url": trail.image_url, "distance_km": trail.distance_km,
            "estimated_duration_hours": trail.estimated_duration_hours,
            "status": hike.status}


def upcoming_events(db, models, trail_id=None, event_id=None):
    counts = db.query(models.HikeRegistration.planned_hike_id,
        func.count(models.HikeRegistration.id).label("total")).filter(
        models.HikeRegistration.status != "cancelled").group_by(models.HikeRegistration.planned_hike_id).subquery()
    query = db.query(models.PlannedHike, models.Hike, models.User, counts.c.total).join(
        models.Hike, models.PlannedHike.hike_id == models.Hike.id).join(
        models.User, models.PlannedHike.user_id == models.User.id).outerjoin(
        counts, counts.c.planned_hike_id == models.PlannedHike.id).filter(
        models.PlannedHike.status == "planned", models.PlannedHike.planned_date > datetime.utcnow(),
        models.User.is_admin.is_(True), models.User.is_active.is_(True))
    if trail_id:
        query = query.filter(models.Hike.id == trail_id)
    if event_id:
        query = query.filter(models.PlannedHike.id == event_id)
    return [event_details(ph, trail, owner, count or 0) for ph, trail, owner, count in
            query.order_by(models.PlannedHike.planned_date).limit(100).all()]


def registrations_for(db, models, user_id):
    active_member(db, models, user_id)
    rows = db.query(models.HikeRegistration, models.PlannedHike, models.Hike).join(
        models.PlannedHike, models.HikeRegistration.planned_hike_id == models.PlannedHike.id).join(
        models.Hike, models.PlannedHike.hike_id == models.Hike.id).filter(
        models.HikeRegistration.user_id == user_id).order_by(models.PlannedHike.planned_date.desc()).all()
    return [{"registration_id": reg.id, "planned_hike_id": ph.id, "hike_id": trail.id,
        "phone_number": reg.phone_number or "", "hike_name": trail.name, "hike_location": trail.location,
        "planned_date": ph.planned_date.isoformat(), "status": reg.status, "event_status": ph.status,
        "payment_status": reg.payment_status, "price": ph.price or 0, "meeting_point": ph.meeting_point,
        "transport_mode": ph.transport_mode, "notes": ph.notes or "", "image_url": trail.image_url,
        "created_at": reg.created_at.isoformat()} for reg, ph, trail in rows]
