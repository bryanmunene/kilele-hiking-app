"""Daraja requests and verified payment settlement. No client-supplied totals."""
import base64
import hashlib
import hmac
import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
import requests
from config import settings
from models.booking import Payment, HikeRegistration


def normalize_phone(phone: str) -> str:
    phone = re.sub(r"[\s+()-]", "", phone)
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif len(phone) == 9:
        phone = "254" + phone
    if not re.fullmatch(r"254[17][0-9]{8}", phone):
        raise ValueError("Enter a valid Kenyan mobile number, such as 0712345678.")
    return phone


def payment_amount(value) -> int:
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount != amount.to_integral_value() or not 1 <= amount <= 150000:
            raise ValueError
        return int(amount)
    except (ValueError, InvalidOperation):
        raise ValueError("M-Pesa payments must be whole shillings between KES 1 and KES 150,000.") from None


class MpesaService:
    def __init__(self):
        self.environment = os.getenv("MPESA_ENVIRONMENT", "sandbox").lower()
        self.consumer_key = os.getenv("MPESA_CONSUMER_KEY", "")
        self.consumer_secret = os.getenv("MPESA_CONSUMER_SECRET", "")
        self.shortcode = os.getenv("MPESA_SHORTCODE", "")
        self.passkey = os.getenv("MPESA_PASSKEY", "")
        self.party_b = os.getenv("MPESA_PARTY_B") or self.shortcode
        self.transaction_type = os.getenv("MPESA_TRANSACTION_TYPE", "CustomerPayBillOnline")
        self.callback_base = os.getenv("MPESA_CALLBACK_BASE_URL") or settings.API_BASE_URL.rstrip("/") + "/api/payments/mpesa/callback"
        self.base_url = "https://api.safaricom.co.ke" if self.environment == "production" else "https://sandbox.safaricom.co.ke"

    @property
    def configured(self):
        callback = urlparse(self.callback_base)
        return bool(
            all([self.consumer_key, self.consumer_secret, self.shortcode, self.passkey, self.party_b])
            and self.environment in {"production", "sandbox"}
            and self.transaction_type in {"CustomerPayBillOnline", "CustomerBuyGoodsOnline"}
            and callback.scheme == "https" and callback.hostname
            and callback.path.rstrip("/") == "/api/payments/mpesa/callback"
            and not callback.hostname.endswith("streamlit.app")
        )

    def callback_signature(self, payment_id: int) -> str:
        return hmac.new(settings.SECRET_KEY.encode(), f"mpesa:{payment_id}".encode(), hashlib.sha256).hexdigest()

    def _auth(self):
        response = requests.get(
            self.base_url + "/oauth/v1/generate",
            params={"grant_type": "client_credentials"},
            auth=(self.consumer_key, self.consumer_secret), timeout=(10, 20),
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _password_payload(self):
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{self.shortcode}{self.passkey}{timestamp}".encode()).decode()
        return {"BusinessShortCode": self.shortcode, "Password": password, "Timestamp": timestamp}

    def initiate(self, payment: Payment) -> dict:
        # Authentication failure cannot have charged the customer. POST timeouts are ambiguous.
        try:
            token = self._auth()
        except (requests.RequestException, ValueError, KeyError):
            return {"status": "failed", "message": "Payment provider authentication failed. Please try later."}
        payload = self._password_payload() | {
            "TransactionType": self.transaction_type, "Amount": payment_amount(payment.amount),
            "PartyA": payment.phone_number, "PartyB": self.party_b, "PhoneNumber": payment.phone_number,
            "CallBackURL": f"{self.callback_base}/{payment.id}/{self.callback_signature(payment.id)}",
            "AccountReference": f"KILELE{payment.registration_id}"[:12], "TransactionDesc": "Hike booking",
        }
        try:
            response = requests.post(self.base_url + "/mpesa/stkpush/v1/processrequest", json=payload,
                                     headers={"Authorization": f"Bearer {token}"}, timeout=(10, 30))
            if response.status_code >= 500:
                return {"status": "unknown", "message": "Payment response delayed. Do not pay again; contact the organizer."}
            result = response.json()
            if response.ok and str(result.get("ResponseCode")) == "0" and result.get("CheckoutRequestID") and result.get("MerchantRequestID"):
                return {"status": "pending", "checkout_request_id": result["CheckoutRequestID"],
                        "merchant_request_id": result["MerchantRequestID"], "message": "Payment prompt sent. Complete it on your phone."}
            return {"status": "failed", "message": "The payment provider declined the request. Please check your number and try again."}
        except (requests.RequestException, ValueError):
            return {"status": "unknown", "message": "Payment response delayed. Do not pay again; contact the organizer."}

    def query(self, checkout_request_id: str) -> dict:
        try:
            token = self._auth()
            response = requests.post(self.base_url + "/mpesa/stkpushquery/v1/query",
                headers={"Authorization": f"Bearer {token}"},
                json=self._password_payload() | {"CheckoutRequestID": checkout_request_id}, timeout=(10, 25))
            response.raise_for_status()
            result = response.json()
            return result if isinstance(result, dict) else {}
        except (requests.RequestException, ValueError, KeyError):
            return {}

    def reconcile(self, db, payment: Payment, callback: dict | None = None) -> Payment:
        if payment.status in {"completed", "failed", "cancelled"} or not payment.checkout_request_id:
            return payment
        if payment.environment != self.environment:
            return payment
        metadata = {}
        if callback:
            if callback.get("CheckoutRequestID") != payment.checkout_request_id or callback.get("MerchantRequestID") != payment.merchant_request_id:
                return payment
            if str(callback.get("ResultCode")) == "0":
                callback_metadata = callback.get("CallbackMetadata")
                if not isinstance(callback_metadata, dict):
                    return payment
                items = callback_metadata.get("Item")
                if not isinstance(items, list):
                    return payment
                metadata = {item.get("Name"): item.get("Value") for item in items if isinstance(item, dict)}
                try:
                    if payment_amount(metadata.get("Amount")) != payment_amount(payment.amount) or normalize_phone(str(metadata.get("PhoneNumber"))) != payment.phone_number:
                        return payment
                except ValueError:
                    return payment
        # A callback alone is never sufficient proof of payment.
        verified = self.query(payment.checkout_request_id)
        code = str(verified.get("ResultCode", ""))
        if code == "0":
            payment.status = "completed"
            if callback:
                payment.transaction_id = str(metadata.get("MpesaReceiptNumber") or "") or None
            if payment.environment == "production":
                registration = db.get(HikeRegistration, payment.registration_id)
                if registration:
                    registration.payment_status = "paid"
                    registration.status = "confirmed"
                    from kilele_core.operations import enqueue
                    from models.booking import PlannedHike
                    from models.hike import Hike
                    planned = db.get(PlannedHike, registration.planned_hike_id)
                    trail = db.get(Hike, planned.hike_id)
                    enqueue(db, f"payment:{payment.id}", registration.user_id, "booking",
                        {"hike": trail.name, "reference": registration.id})
        elif code in {"1", "1032", "1037", "2001", "1025", "1019", "9999"}:
            payment.status = "cancelled" if code == "1032" else "failed"
        payment.updated_at = datetime.utcnow()
        db.commit()
        return payment


mpesa_service = MpesaService()
