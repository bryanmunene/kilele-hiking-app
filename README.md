# Kilele

Kilele is a Kenyan trail-discovery and hike-tracking app built with Streamlit and SQLAlchemy. Explore curated trails, compare routes, plan a hike, save favourites, record reviews, and import activity files from popular outdoor devices.

**Live app:** https://kilele-hiking-appgit-cnrnmlnmkgku6xjzrrxzcg.streamlit.app/

## Highlights

- Discover Kenyan trails with distance, elevation, duration, and difficulty filters
- Browse an interactive trail map and carry selected routes across pages
- Save trails, add reviews, plan outings, and track achievements
- Import GPX, FIT, and TCX files from Garmin, COROS, Suunto, and other devices
- Optional Strava integration through a separately deployed, credential-safe backend
- Responsive, nature-inspired interface with a compact task-based navigation system
- Password hashing, bounded persistent sessions, 2FA support, and role-based admin tools

## Run locally

```bash
git clone https://github.com/bryanmunene/kilele-hiking-app.git
cd kilele-hiking-app
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r frontend/requirements.txt
cd frontend
python seed_database.py
streamlit run Home.py
```

Open `http://localhost:8501`. The seed command creates trail and gear catalogue data only; create your own account from the app.

## Configuration

The app works without external services. Optional integrations are read from environment variables or Streamlit secrets:

```toml
DATABASE_URL = "postgresql://..."        # defaults to local SQLite
API_BASE_URL = "https://api.example.com" # optional Strava service
CLOUDINARY_CLOUD_NAME = "..."            # optional image uploads
CLOUDINARY_API_KEY = "..."
CLOUDINARY_API_SECRET = "..."
```

Never commit real secrets. Add them in the deployment settings.

## Project layout

```text
frontend/
  Home.py              Main Streamlit entry point
  pages/               App pages
  services.py          Database-backed business logic
  models.py            SQLAlchemy models
  database.py          Connection and safe schema upgrades
  utils/               Activity-file parsers and helpers
backend/                Optional integration API
```

## Verification

```bash
python -m compileall -q frontend
```

The project also supports Streamlit's `AppTest` framework for page-level smoke tests.
