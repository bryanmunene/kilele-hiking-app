import base64
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from email import message_from_bytes
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.env = patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///" + (Path(cls.temp.name) / "integrations.db").as_posix(),
            "ENVIRONMENT": "development", "DEBUG": "False",
        })
        cls.env.start()
        sys.path.insert(0, str(ROOT / "backend"))
        from test_backend_imports import clear_backend_modules
        clear_backend_modules()
        import main
        import database
        import auth_actions
        import auth
        import config
        import email_service
        import mpesa_service
        import strava_service
        from models.booking import Payment, HikeRegistration, PlannedHike
        from models.hike import Hike
        from models.user import User
        from models.session_token import SessionToken
        from models.auth_action import AuthActionToken
        from fastapi.testclient import TestClient
        cls.modules = SimpleNamespace(**locals())
        cls.client = TestClient(main.app)
        main.limiter.enabled = False

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.modules.database.engine.dispose()
        cls.env.stop()
        cls.temp.cleanup()

    def setUp(self):
        m = self.modules
        with m.database.get_db_context() as db:
            for table in reversed(m.database.Base.metadata.sorted_tables):
                db.execute(table.delete())
            self.user = m.User(username="hiker", email="hiker@example.com", hashed_password=m.auth.get_password_hash("Testing-pass-42"), is_admin=True)
            self.other = m.User(username="other", email="other@example.com", hashed_password="unused")
            self.hike = m.Hike(name="Trail", location="Kenya", difficulty="Easy", distance_km=5, estimated_duration_hours=2)
            db.add_all([self.user, self.other, self.hike])
            db.flush()
            self.ids = (self.user.id, self.other.id, self.hike.id)
            self.planned = m.PlannedHike(user_id=self.user.id, hike_id=self.hike.id, planned_date=datetime.utcnow() + timedelta(days=10), price=100, max_participants=3)
            db.add(self.planned)
            db.flush()
            self.planned_id = self.planned.id
            for user_id, token in [(self.user.id, "test-session"), (self.other.id, "other-session")]:
                db.add(m.SessionToken(user_id=user_id, token=token, expires_at=datetime.utcnow() + timedelta(days=1)))
        self.headers = {"X-Session-Token": "test-session"}

    def mpesa(self, environment="production"):
        service = self.modules.mpesa_service.mpesa_service
        return patch.multiple(service, consumer_key="test-key", consumer_secret="test-secret",
            shortcode="174379", passkey="test-passkey", party_b="174379", environment=environment,
            callback_base="https://kilele-hiking-api.onrender.com/api/payments/mpesa/callback")

    def checkout(self):
        service = self.modules.mpesa_service.mpesa_service
        with patch.object(service, "initiate", return_value={"status": "pending", "checkout_request_id": "checkout-1", "merchant_request_id": "merchant-1", "message": "Prompt sent"}):
            response = self.client.post("/api/payments/checkout", headers=self.headers,
                json={"planned_hike_id": self.planned_id, "phone_number": "0712345678", "amount": 1})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_checkout_uses_database_price_and_deduplicates_retries(self):
        with self.mpesa():
            first = self.checkout()
            second = self.checkout()
        self.assertEqual(first["payment_id"], second["payment_id"])
        with self.modules.database.get_db_context() as db:
            payment = db.get(self.modules.Payment, first["payment_id"])
            self.assertEqual(payment.amount, 100)
            self.assertEqual(payment.phone_number, "254712345678")
            self.assertEqual(db.query(self.modules.Payment).count(), 1)
        denied = self.client.post(f"/api/payments/registrations/{first['registration_id']}/status", headers={"X-Session-Token": "other-session"})
        self.assertEqual(denied.status_code, 404)

    def test_production_callback_requires_signature_and_provider_confirmation(self):
        m = self.modules
        with self.mpesa():
            payment = self.checkout()
            signature = m.mpesa_service.mpesa_service.callback_signature(payment["payment_id"])
            path = f"/api/payments/mpesa/callback/{payment['payment_id']}/{signature}"
            payload = {"Body": {"stkCallback": {
                "CheckoutRequestID": "checkout-1", "MerchantRequestID": "merchant-1", "ResultCode": 0,
                "CallbackMetadata": {"Item": [{"Name": "Amount", "Value": 100}, {"Name": "PhoneNumber", "Value": 254712345678}, {"Name": "MpesaReceiptNumber", "Value": "TEST-RECEIPT"}]},
            }}}
            self.assertEqual(self.client.post(path + "wrong", json=payload).status_code, 403)
            with patch.object(m.mpesa_service.mpesa_service, "query", return_value={}):
                self.assertEqual(self.client.post(path, json=payload).status_code, 200)
            with m.database.get_db_context() as db:
                self.assertEqual(db.get(m.HikeRegistration, payment["registration_id"]).payment_status, "unpaid")
            with patch.object(m.mpesa_service.mpesa_service, "query", return_value={"ResultCode": 0}):
                self.assertEqual(self.client.post(path, json=payload).status_code, 200)
                self.assertEqual(self.client.post(path, json=payload).status_code, 200)
            with m.database.get_db_context() as db:
                self.assertEqual(db.get(m.Payment, payment["payment_id"]).transaction_id, "TEST-RECEIPT")
                self.assertEqual(db.get(m.HikeRegistration, payment["registration_id"]).status, "confirmed")

    def test_sandbox_cannot_confirm_paid_booking_and_non_admin_is_blocked(self):
        m = self.modules
        with self.mpesa("sandbox"):
            payment = self.checkout()
            with patch.object(m.mpesa_service.mpesa_service, "query", return_value={"ResultCode": "0"}):
                result = self.client.post(f"/api/payments/registrations/{payment['registration_id']}/status", headers=self.headers)
                self.assertEqual(result.json()["status"], "completed")
            denied = self.client.post("/api/payments/checkout", headers={"X-Session-Token": "other-session"}, json={"planned_hike_id": self.planned_id, "phone_number": "0712345678"})
            self.assertEqual(denied.status_code, 503)
            with m.database.get_db_context() as db:
                self.assertEqual(db.get(m.HikeRegistration, payment["registration_id"]).payment_status, "unpaid")

    def test_cancelled_payment_can_retry_and_completed_payment_cannot(self):
        service = self.modules.mpesa_service.mpesa_service
        with self.mpesa():
            first = self.checkout()
            with patch.object(service, "query", return_value={"ResultCode": 1032}):
                result = self.client.post(f"/api/payments/registrations/{first['registration_id']}/status", headers=self.headers)
            self.assertEqual(result.json()["status"], "cancelled")
            second = self.checkout()
            self.assertNotEqual(first["payment_id"], second["payment_id"])
            with patch.object(service, "query", return_value={"ResultCode": 0}):
                self.client.post(f"/api/payments/registrations/{first['registration_id']}/status", headers=self.headers)
            response = self.client.post("/api/payments/checkout", headers=self.headers, json={"planned_hike_id": self.planned_id, "phone_number": "0712345678"})
            self.assertEqual(response.status_code, 409)

    def test_strava_sdk_activity_types_are_persisted_correctly(self):
        import json
        from stravalib.model import SummaryActivity
        from models.strava import StravaToken
        activity = SummaryActivity.model_validate({
            "id": 123, "name": "Trail walk", "type": "Hike", "sport_type": "Hike",
            "distance": 2500, "moving_time": 1800, "elapsed_time": 1900,
            "total_elevation_gain": 120, "start_date": "2026-08-01T10:00:00Z",
            "start_date_local": "2026-08-01T13:00:00Z",
            "start_latlng": [-1, 36], "end_latlng": [-1.01, 36.01],
        })
        with self.modules.database.get_db_context() as db:
            token = StravaToken(user_id=self.ids[0], athlete_id=10, access_token="test", refresh_token="test", expires_at=datetime.utcnow())
            db.add(token)
            db.flush()
            saved = self.modules.strava_service.strava_service._create_activity_from_strava(activity, token.id, self.ids[0], db)
            self.assertEqual(saved.moving_time, 1800)
            self.assertEqual(saved.activity_type, "Hike")
            self.assertEqual(saved.distance, 2500)
            self.assertEqual(json.loads(saved.start_latlng), [-1, 36])

    def test_phone_amount_and_missing_credentials_validation(self):
        m = self.modules.mpesa_service
        for phone in ["0712345678", "+254 712 345 678", "712345678"]:
            self.assertEqual(m.normalize_phone(phone), "254712345678")
        for phone in ["254abcdefghi", "123", "254212345678"]:
            with self.assertRaises(ValueError):
                m.normalize_phone(phone)
        for value in [0, 1.5, float("nan"), float("inf"), 150001]:
            with self.assertRaises(ValueError):
                m.payment_amount(value)
        with patch.object(m.mpesa_service, "consumer_key", ""):
            response = self.client.post("/api/payments/checkout", headers=self.headers, json={"planned_hike_id": self.planned_id, "phone_number": "0712345678"})
            self.assertEqual(response.status_code, 503)

    def test_strava_state_is_user_bound_single_use_and_expiring(self):
        m = self.modules
        service = m.strava_service.strava_service
        with m.database.get_db_context() as db:
            token = m.auth_actions.issue_action(db, self.ids[0], "strava")
        with patch.object(service, "exchange_code_for_token", return_value=SimpleNamespace(athlete_id=42)) as exchange:
            payload = {"state": token, "code": "test-code", "scope": "read,activity:read"}
            denied = self.client.post("/api/strava/callback", headers={"X-Session-Token": "other-session"}, json=payload)
            self.assertEqual(denied.status_code, 400)
            self.assertEqual(self.client.post("/api/strava/callback", headers=self.headers, json=payload).status_code, 200)
            self.assertEqual(self.client.post("/api/strava/callback", headers=self.headers, json=payload).status_code, 400)
            self.assertEqual(exchange.call_count, 1)
        with m.database.get_db_context() as db:
            expired = m.auth_actions.issue_action(db, self.ids[0], "strava", minutes=-1)
        self.assertEqual(self.client.post("/api/strava/callback", headers=self.headers, json={"state": expired, "code": "test"}).status_code, 400)
        with patch.object(service, "is_configured", False):
            self.assertEqual(self.client.get("/api/strava/connect", headers=self.headers).status_code, 503)

    def test_password_recovery_sends_link_and_revokes_sessions_and_old_jwts(self):
        m = self.modules
        old_jwt = m.auth.create_access_token({"sub": "hiker"})
        with patch.object(m.email_service.EmailService, "configured", new_callable=unittest.mock.PropertyMock, return_value=True), patch.object(m.email_service.email_service, "send_password_reset", return_value=True) as send:
            known = self.client.post("/api/v1/auth/forgot-password", json={"email": "hiker@example.com"})
            unknown = self.client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})
            self.assertEqual(known.json(), unknown.json())
            token = send.call_args.args[1]
            self.assertEqual(send.call_count, 1)
            self.client.post("/api/v1/auth/forgot-password", json={"email": "hiker@example.com"})
            self.assertEqual(send.call_count, 1)
        payload = {"token": token, "password": "Updated-testing-pass-42"}
        self.assertEqual(self.client.post("/api/v1/auth/reset-password", json=payload).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/reset-password", json=payload).status_code, 400)
        self.assertEqual(self.client.get("/api/strava/stats", headers=self.headers).status_code, 401)
        self.assertEqual(self.client.get("/api/strava/stats", headers={"Authorization": f"Bearer {old_jwt}"}).status_code, 401)
        fresh_jwt = m.auth.create_access_token({"sub": "hiker"})
        self.assertEqual(self.client.get("/api/strava/stats", headers={"Authorization": f"Bearer {fresh_jwt}"}).status_code, 200)

    def test_gmail_uses_https_refresh_and_correct_mime_and_failures_are_false(self):
        m = self.modules
        with patch.multiple(m.config.settings, GMAIL_CLIENT_ID="test-id", GMAIL_CLIENT_SECRET="test-secret", GMAIL_REFRESH_TOKEN="test-refresh", FROM_EMAIL="owner@gmail.com"):
            token = Mock(status_code=200)
            token.json.return_value = {"access_token": "temporary-token"}
            delivered = Mock(status_code=200)
            delivered.json.return_value = {"id": "message-id"}
            with patch.object(m.email_service.requests, "post", side_effect=[token, delivered]) as post:
                self.assertTrue(m.email_service.email_service.send_password_reset("hiker@example.com", "reset-test-token", "<script>"))
                mime = message_from_bytes(base64.urlsafe_b64decode(post.call_args.kwargs["json"]["raw"]))
                self.assertEqual(mime["To"], "hiker@example.com")
                html = mime.get_payload()[1].get_payload(decode=True).decode()
                self.assertIn("/Login?reset_token=reset-test-token", html)
                self.assertNotIn("<script>", html)
                self.assertIn("gmail.googleapis.com", post.call_args.args[0])
            with patch.object(m.email_service.requests, "post", side_effect=m.email_service.requests.Timeout):
                self.assertFalse(m.email_service.email_service.send_email("hiker@example.com", "Test", "Test"))
