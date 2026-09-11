"""Create only an explicitly named local SQLite database for browser tests."""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

if len(sys.argv) != 2 or not sys.argv[1].endswith(".db"):
    raise SystemExit("Pass a local .db path for isolated browser fixtures.")
path = Path(sys.argv[1]).resolve()
os.environ["DATABASE_URL"] = "sqlite:///" + path.as_posix()
os.environ["ENVIRONMENT"] = "development"
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "frontend"))
from database import get_db
from seed_database import seed_database
from auth import hash_password
from models import User, PlannedHike, Hike

seed_database()
with get_db() as db:
    user = db.query(User).filter_by(username="layout_tester").first()
    if not user:
        user = User(username="layout_tester", email="layout@example.com",
                    full_name="Layout Test User", is_admin=True,
                    hashed_password=hash_password("Kilele-ui-only-47!"))
        db.add(user)
        db.flush()
    trail = db.query(Hike).first()
    if not db.query(User).filter_by(username="journey_member").first():
        db.add(User(username="journey_member", email="journey@example.com",
                    full_name="Journey Test Member", is_admin=False,
                    hashed_password=hash_password("Kilele-ui-only-47!")))
    if not db.query(PlannedHike).filter_by(user_id=user.id).first():
        for price in [0, 2500]:
            db.add(PlannedHike(user_id=user.id, hike_id=trail.id, planned_date=datetime.utcnow() + timedelta(days=7),
                               price=price, max_participants=20, notes="Weekend group hike with a meeting point and a full-day trail itinerary."))
print("Local browser fixtures ready.")
