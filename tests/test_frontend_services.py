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
        for module_name in ["database", "models", "services", "config", "auth", "main"]:
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
            for table in reversed(models.Base.metadata.sorted_tables):
                db.execute(table.delete())

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
        self.assertTrue(services.update_goal_progress(goal["id"], 10))
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
