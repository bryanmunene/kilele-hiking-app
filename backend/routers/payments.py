"""Authenticated checkout and signed, independently verified Daraja callbacks."""
from datetime import datetime
import hmac
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from auth import get_current_active_user
from database import get_db, get_db_context
from models.booking import HikeRegistration, Payment, PlannedHike
from models.user import User
from mpesa_service import mpesa_service, normalize_phone, payment_amount
from rate_limiter import limiter
from kilele_core.bookings import BookingError, ensure_capacity, lock_open_hike
from types import SimpleNamespace

booking_models = SimpleNamespace(PlannedHike=PlannedHike, HikeRegistration=HikeRegistration, User=User)

router = APIRouter(prefix="/api/payments", tags=["payments"])


class CheckoutRequest(BaseModel):
    planned_hike_id: int = Field(gt=0)
    phone_number: str = Field(min_length=9, max_length=30)


def payment_result(payment, message=None):
    return {"payment_id": payment.id, "registration_id": payment.registration_id,
            "status": payment.status, "environment": payment.environment,
            "receipt": payment.transaction_id, "message": message}


@router.get("/config")
def configuration(user: User = Depends(get_current_active_user)):
    return {"available": mpesa_service.configured and mpesa_service.environment == "production",
            "sandbox_available": mpesa_service.configured and mpesa_service.environment == "sandbox" and user.is_admin,
            "environment": mpesa_service.environment}


@router.post("/checkout")
@limiter.limit("5/minute")
def checkout(request: Request, body: CheckoutRequest, db: Session = Depends(get_db),
             user: User = Depends(get_current_active_user)):
    if not mpesa_service.configured or (mpesa_service.environment != "production" and not user.is_admin):
        raise HTTPException(503, "Online payments are not available yet.")
    try:
        phone = normalize_phone(body.phone_number)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    # Serialize capacity checks and retries on the same hike across both services.
    try:
        hike = lock_open_hike(db, booking_models, body.planned_hike_id)
    except BookingError as exc:
        raise HTTPException(400, str(exc)) from None
    try:
        amount = payment_amount(hike.price)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    registration = db.query(HikeRegistration).filter_by(planned_hike_id=hike.id, user_id=user.id).first()
    if registration and registration.payment_status == "paid":
        raise HTTPException(409, "This registration is already paid.")
    if registration:
        previous = db.query(Payment).filter_by(registration_id=registration.id).order_by(Payment.id.desc()).first()
        if previous and previous.status in {"pending", "unknown"}:
            return payment_result(previous, "A payment is already in progress. Check its status before trying again.")
        if previous and previous.status == "completed" and previous.environment == "production":
            raise HTTPException(409, "This payment is already completed.")
    try:
        ensure_capacity(db, booking_models, hike, registration)
    except BookingError as exc:
        raise HTTPException(409, str(exc)) from None
    if not registration:
        registration = HikeRegistration(planned_hike_id=hike.id, user_id=user.id)
        db.add(registration)
    registration.status = "pending"
    registration.phone_number = phone
    db.flush()
    payment = Payment(registration_id=registration.id, user_id=user.id, phone_number=phone,
                      amount=amount, environment=mpesa_service.environment)
    db.add(payment)
    db.commit()
    result = mpesa_service.initiate(payment)
    payment.status = result["status"]
    payment.checkout_request_id = result.get("checkout_request_id")
    payment.merchant_request_id = result.get("merchant_request_id")
    db.commit()
    return payment_result(payment, result["message"])


@router.post("/registrations/{registration_id}/status")
@limiter.limit("10/minute")
def refresh_payment(request: Request, registration_id: int, db: Session = Depends(get_db),
                    user: User = Depends(get_current_active_user)):
    registration = db.query(HikeRegistration).filter_by(id=registration_id, user_id=user.id).first()
    if not registration:
        raise HTTPException(404, "Registration not found.")
    payment = db.query(Payment).filter_by(registration_id=registration.id, user_id=user.id).order_by(Payment.id.desc()).with_for_update().first()
    if not payment:
        return {"status": "unpaid", "registration_id": registration.id}
    return payment_result(mpesa_service.reconcile(db, payment))


def reconcile_callback(payment_id, callback):
    with get_db_context() as db:
        payment = db.query(Payment).filter_by(id=payment_id).with_for_update().first()
        if payment:
            mpesa_service.reconcile(db, payment, callback)


@router.post("/mpesa/callback/{payment_id}/{signature}")
def callback(payment_id: int, signature: str, body: dict, background: BackgroundTasks):
    if not hmac.compare_digest(signature, mpesa_service.callback_signature(payment_id)):
        raise HTTPException(403, "Invalid callback.")
    envelope = body.get("Body")
    data = envelope.get("stkCallback") if isinstance(envelope, dict) else None
    if not isinstance(data, dict) or not data.get("CheckoutRequestID"):
        raise HTTPException(400, "Invalid callback payload.")
    background.add_task(reconcile_callback, payment_id, data)
    return {"ResultCode": 0, "ResultDesc": "Accepted"}
