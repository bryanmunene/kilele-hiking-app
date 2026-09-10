import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"


class FrontendServiceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        database_path = Path(cls.tempdir.name) / "kilele-test.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
        sys.path.insert(0, str(FRONTEND_DIR))
        for module_name in ["database", "models", "services", "config", "auth", "main", "activity_import", "cloudinary_service"]:
            sys.modules.pop(module_name, None)

        global database, models, services
        import database
        import models
        import services

        database.init_database()

    @classmethod
    def tearDownClass(cls):
        database.engine.dispose()
        cls.tempdir.cleanup()

    def setUp(self):
        with database.get_db() as db:
            from kilele_core.security import metadata
            for table in reversed(metadata.sorted_tables):
                db.execute(table.delete())
            for table in reversed(models.Base.metadata.sorted_tables):
                db.execute(table.delete())

    def seed_booking(self, capacity=1):
        owner, guest, trail = self.seed_users_and_hike()
        with database.get_db() as db:
            hike = models.PlannedHike(user_id=owner, hike_id=trail,
                planned_date=datetime.utcnow() + timedelta(days=10), price=0,
                max_participants=capacity)
            db.add(hike)
            db.flush()
            return owner, guest, hike.id

    def test_booking_cancellation_releases_capacity_and_rebooking_reuses_record(self):
        from sqlalchemy import select
        from kilele_core.operations import outbox
        owner, guest, hike = self.seed_booking()
        first = services.register_for_hike(guest, hike, "254700000000")
        self.assertNotIn("error", first)
        self.assertIn("error", services.register_for_hike(owner, hike, "254700000001"))
        self.assertIn("error", services.cancel_registration(owner, first["registration_id"]))
        self.assertNotIn("error", services.cancel_registration(guest, first["registration_id"]))
        self.assertNotIn("error", services.cancel_registration(guest, first["registration_id"]))
        again = services.register_for_hike(guest, hike, "254700000002")
        self.assertEqual(again["registration_id"], first["registration_id"])
        with database.get_db() as db:
            self.assertEqual(db.query(models.HikeRegistration).count(), 1)
            self.assertEqual(len(db.execute(select(outbox)).all()), 3)

    def test_organizer_cancellation_preserves_ledger_and_notifies_once(self):
        from sqlalchemy import select
        from kilele_core.operations import outbox
        owner, guest, hike = self.seed_booking()
        first = services.register_for_hike(guest, hike, "254700000000")
        self.assertIn("error", services.delete_planned_hike(hike, owner))
        self.assertIn("error", services.update_planned_hike_status(hike, "cancelled", guest))
        self.assertIn("error", services.update_planned_hike_status(hike, "completed", owner))
        self.assertIn("error", services.update_planned_hike_status(hike, "planned", owner, changes={"price": 100}))
        self.assertNotIn("error", services.update_planned_hike_status(hike, "cancelled", owner))
        services.update_planned_hike_status(hike, "cancelled", owner)
        with database.get_db() as db:
            self.assertEqual(db.get(models.HikeRegistration, first["registration_id"]).status, "cancelled")
            self.assertEqual(len(db.execute(select(outbox)).all()), 2)
        self.assertNotIn("error", services.update_planned_hike_status(hike, "planned", owner))
        with database.get_db() as db:
            self.assertEqual(db.get(models.HikeRegistration, first["registration_id"]).status, "cancelled")

    def test_account_export_and_erasure_do_not_affect_another_member(self):
        import json
        from kilele_core.operations import export_account, erase_account, submit_report
        owner, guest, hike = self.seed_booking()
        registration = services.register_for_hike(guest, hike, "254700000000")
        conversation = services.create_conversation([owner, guest])
        services.send_message(guest, conversation["id"], "Private meeting details")
        services.send_message(owner, conversation["id"], "Other member message")
        with database.get_db() as db:
            db.add(models.SessionToken(user_id=guest, token="private-session-secret", expires_at=datetime.utcnow() + timedelta(days=1)))
            db.add(models.Payment(user_id=guest, registration_id=registration["registration_id"], amount=100, phone_number="254700000000"))
            submit_report(db, guest, "support", "Please help with my booking.")
        with database.get_db() as db:
            user = db.get(models.User, guest)
            exported = json.dumps(export_account(db, user), default=str)
            self.assertIn("Private meeting details", exported)
            self.assertNotIn("Other member message", exported)
            self.assertNotIn("private-session-secret", exported)
            self.assertNotIn("hashed_password", exported)
            erase_account(db, user)
        with database.get_db() as db:
            user = db.get(models.User, guest)
            self.assertFalse(user.is_active)
            self.assertEqual(user.full_name, "Deleted account")
            self.assertEqual(db.query(models.SessionToken).filter_by(user_id=guest).count(), 0)
            self.assertEqual(db.query(models.Payment).one().phone_number, "")
            self.assertEqual(db.get(models.HikeRegistration, registration["registration_id"]).status, "cancelled")
            self.assertEqual(db.query(models.Message).filter_by(sender_id=guest).one().content, "[deleted]")
            self.assertEqual(db.query(models.Message).filter_by(sender_id=owner).one().content, "Other member message")
            self.assertTrue(db.get(models.User, owner).is_active)
            with self.assertRaises(ValueError):
                erase_account(db, db.get(models.User, owner))

    def test_authenticator_changes_require_credentials_and_revoke_sessions(self):
        import auth
        import pyotp
        owner, guest, _ = self.seed_booking()
        with database.get_db() as db:
            db.get(models.User, guest).hashed_password = auth.hash_password("Test-only-pass-47!")
            db.add(models.SessionToken(user_id=guest, token="old-session", expires_at=datetime.utcnow() + timedelta(days=1)))
        with self.assertRaises(ValueError):
            auth.setup_2fa(guest, "wrong")
        secret, _ = auth.setup_2fa(guest, "Test-only-pass-47!")
        self.assertFalse(auth.enable_2fa(guest))
        self.assertTrue(auth.enable_2fa(guest, code=pyotp.TOTP(secret).now()))
        with database.get_db() as db:
            self.assertEqual(db.query(models.SessionToken).filter_by(user_id=guest).count(), 0)
        with self.assertRaises(ValueError):
            auth.setup_2fa(guest, "Test-only-pass-47!")
        self.assertFalse(auth.disable_2fa(guest, "wrong", pyotp.TOTP(secret).now()))
        self.assertTrue(auth.disable_2fa(guest, "Test-only-pass-47!", pyotp.TOTP(secret).now()))

    def test_profile_and_owned_mutations_reject_privilege_or_owner_changes(self):
        owner, guest, _ = self.seed_booking()
        services.update_user_profile(guest, {"full_name": "Updated Name", "is_admin": True, "email": "attacker@example.com"})
        goal = services.create_goal(guest, "Walk", "distance", 10)
        self.assertFalse(services.update_goal_progress(goal["id"], 10, user_id=owner))
        with database.get_db() as db:
            user = db.get(models.User, guest)
            self.assertFalse(user.is_admin)
            self.assertEqual(user.email, "amina@example.com")

    def test_block_stops_messages_in_both_directions(self):
        from kilele_core.operations import set_block
        owner, guest, _ = self.seed_booking()
        conversation = services.create_conversation([owner, guest])
        with database.get_db() as db:
            set_block(db, guest, owner, True)
        for sender in (owner, guest):
            with self.assertRaises(ValueError):
                services.send_message(sender, conversation["id"], "Blocked message")
        with database.get_db() as db:
            set_block(db, guest, owner, False)
        self.assertIn("id", services.send_message(owner, conversation["id"], "Allowed again"))

    def test_manage_hikes_renders_bookings_without_detached_records(self):
        from streamlit.testing.v1 import AppTest
        owner, guest, hike = self.seed_booking()
        services.register_for_hike(guest, hike, "254700000000")
        with database.get_db() as db:
            db.add(models.SessionToken(user_id=owner, token="admin-ui-test", expires_at=datetime.utcnow() + timedelta(days=1)))
        page = next((FRONTEND_DIR / "pages").glob("22_*.py"))
        app = AppTest.from_file(str(page), default_timeout=30)
        app.session_state["session_token"] = "admin-ui-test"
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertTrue(any("Elephant Hill" in item.label for item in app.expander))

    def seed_users_and_hike(self):
        with database.get_db() as db:
            nesh = models.User(
                username="Nesh",
                email="nesh@example.com",
                hashed_password="hash",
                full_name="Nesh Explorer",
                is_admin=True,
            )
            amina = models.User(
                username="Amina",
                email="amina@example.com",
                hashed_password="hash",
                full_name="Amina Hiker",
            )
            hike = models.Hike(
                name="Elephant Hill",
                location="Aberdare Range",
                difficulty="Hard",
                distance_km=18.0,
                elevation_gain_m=900.0,
                estimated_duration_hours=7.5,
                trail_type="Out and Back",
                best_season="Dry season",
                latitude=-0.650,
                longitude=36.650,
            )
            db.add_all([nesh, amina, hike])
            db.flush()
            return nesh.id, amina.id, hike.id

    def test_reviews_bookmarks_follows_feed_and_stats_share_expected_shape(self):
        user_id, other_user_id, hike_id = self.seed_users_and_hike()

        bookmark = services.create_bookmark(user_id, hike_id, notes="Carry rain gear")
        self.assertEqual(bookmark["notes"], "Carry rain gear")
        self.assertEqual(bookmark["hike"]["name"], "Elephant Hill")

        review = services.create_review(
            user_id=user_id,
            hike_id=hike_id,
            rating=5,
            title="Big climb, bigger views",
            comment="A demanding but rewarding route.",
            difficulty_rating=4,
            conditions="Muddy near the bamboo zone",
            visited_date="2026-08-20T00:00:00",
        )
        self.assertEqual(review["user_id"], user_id)
        self.assertEqual(review["title"], "Big climb, bigger views")
        self.assertEqual(review["difficulty_rating"], 4)
        self.assertEqual(review["conditions"], "Muddy near the bamboo zone")
        self.assertEqual(review["username"], "Nesh")

        filtered_reviews = services.get_reviews(hike_id=hike_id, user_id=user_id)
        self.assertEqual(len(filtered_reviews), 1)

        follow = services.follow_user(user_id, other_user_id)
        self.assertEqual(follow["following_user_id"], other_user_id)
        self.assertEqual(services.get_following(user_id)[0]["following_username"], "Amina")
        self.assertEqual(services.get_followers(other_user_id)[0]["follower_username"], "Nesh")

        services.create_session(
            user_id,
            {
                "hike_id": hike_id,
                "status": "completed",
                "distance_covered_km": 18.0,
                "duration_hours": 7.5,
                "elevation_gain_m": 900.0,
                "ended_at": datetime.utcnow(),
            },
        )

        stats = services.get_user_stats(user_id)
        self.assertEqual(stats["total_distance_km"], 18.0)
        self.assertEqual(stats["total_elevation_m"], 900.0)
        self.assertEqual(stats["hard_hikes"], 1)

        feed = services.get_activity_feed(user_id)
        self.assertTrue(any(item["activity_type"] == "completed_hike" for item in feed))
        self.assertTrue(services.delete_bookmark(user_id, hike_id))

    def test_goals_achievements_comments_and_legacy_session_imports_work(self):
        user_id, _, hike_id = self.seed_users_and_hike()

        imported_session = services.create_session(
            user_id,
            hike_id,
            distance_km=6.0,
            duration_minutes=90,
            elevation_gain_m=200,
            status="completed",
        )
        self.assertEqual(imported_session["distance_covered_km"], 6.0)
        self.assertEqual(imported_session["duration_hours"], 1.5)
        self.assertEqual(imported_session["status"], "completed")

        achievements = services.get_user_achievements(user_id)
        first_steps = next(item for item in achievements if item["name"] == "First Steps")
        self.assertTrue(first_steps["earned"])
        self.assertEqual(first_steps["progress"], 100)

        deadline = (datetime.utcnow() + timedelta(days=30)).isoformat()
        goal = services.create_goal(user_id, "Walk 10km", "distance", 10, deadline=deadline)
        self.assertIn("id", goal)
        self.assertTrue(services.update_goal_progress(goal["id"], 10, user_id=user_id))
        completed_goal = services.get_user_goals(user_id)[0]
        self.assertEqual(completed_goal["status"], "completed")
        self.assertIsNotNone(completed_goal["completed_at"])

        parent = services.add_trail_comment(hike_id, user_id, "Watch for slick roots after rain.")
        reply = services.add_trail_comment(hike_id, user_id, "The upper section dries faster.", parent_id=parent["id"])
        comments = services.get_trail_comments(hike_id)
        self.assertEqual({comment["id"] for comment in comments}, {parent["id"], reply["id"]})
        self.assertIn("parent_id", comments[0])

    def test_messaging_services_create_reuse_send_and_mark_read(self):
        user_id, other_user_id, _ = self.seed_users_and_hike()

        conversation = services.create_conversation([user_id, other_user_id, other_user_id])
        duplicate = services.create_conversation([other_user_id, user_id])
        self.assertEqual(conversation["id"], duplicate["id"])

        with self.assertRaises(ValueError):
            services.send_message(user_id, conversation["id"], "   ")

        message = services.send_message(user_id, conversation["id"], "See you on the ridge.")
        self.assertIn("id", message)

        recipient_conversations = services.get_user_conversations(other_user_id)
        self.assertEqual(len(recipient_conversations), 1)
        self.assertEqual(recipient_conversations[0]["unread_count"], 1)
        self.assertEqual(recipient_conversations[0]["participants"][0]["username"], "Nesh")
        self.assertEqual(
            recipient_conversations[0]["last_message"]["content"],
            "See you on the ridge.",
        )

        messages = services.get_conversation_messages(conversation["id"], other_user_id)
        self.assertEqual(messages[0]["sender_username"], "Nesh")
        self.assertEqual(messages[0]["content"], "See you on the ridge.")

        recipient_conversations = services.get_user_conversations(other_user_id)
        self.assertEqual(recipient_conversations[0]["unread_count"], 0)

        search_results = services.search_users("nesh", exclude_user_id=other_user_id)
        self.assertEqual(search_results[0]["username"], "Nesh")
        self.assertEqual(services.search_users("nesh", exclude_user_id=user_id), [])

    def test_activity_import_saves_completed_session_without_trail_and_deduplicates(self):
        from activity_import import import_activity
        user_id, _, _ = self.seed_users_and_hike()
        content = b'''<gpx version="1.1" creator="test"><trk><trkseg>
          <trkpt lat="-1.0" lon="36.0"><ele>100</ele><time>2026-08-01T10:00:00Z</time></trkpt>
          <trkpt lat="-1.01" lon="36.01"><ele>150</ele><time>2026-08-01T11:00:00Z</time></trkpt>
        </trkseg></trk></gpx>'''
        first = import_activity(user_id, "walk.gpx", content)
        duplicate = import_activity(user_id, "renamed.gpx", content)
        self.assertFalse(first["duplicate"])
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(first["session_id"], duplicate["session_id"])
        with database.get_db() as db:
            session = db.get(models.HikeSession, first["session_id"])
            self.assertIsNone(session.hike_id)
            self.assertFalse(session.is_active)
            self.assertEqual(session.status, "completed")
            self.assertGreater(session.distance_covered_km, 1)
            self.assertEqual(session.duration_hours, 1)
            self.assertEqual(session.elevation_gain_m, 50)

    def test_activity_import_rejects_invalid_empty_and_oversize_files(self):
        from activity_import import import_activity
        user_id, _, _ = self.seed_users_and_hike()
        for content in [b"", b"not a gpx file", b"<gpx></gpx>", b"x" * (10 * 1024 * 1024 + 1)]:
            with self.assertRaises(ValueError):
                import_activity(user_id, "walk.gpx", content)
        with database.get_db() as db:
            self.assertEqual(db.query(models.HikeSession).count(), 0)

    def test_phone_photo_orientation_and_invalid_image_fallback(self):
        import base64
        import io
        from PIL import Image
        from cloudinary_service import uploaded_image_to_data_url
        source = Image.new("RGB", (80, 40), "red")
        exif = source.getexif()
        exif[274] = 6
        upload = io.BytesIO()
        source.save(upload, format="JPEG", exif=exif)
        encoded = uploaded_image_to_data_url(upload)
        decoded = Image.open(io.BytesIO(base64.b64decode(encoded.split(",", 1)[1])))
        self.assertEqual(decoded.size, (40, 80))
        self.assertIsNone(uploaded_image_to_data_url(io.BytesIO(b"not an image")))
