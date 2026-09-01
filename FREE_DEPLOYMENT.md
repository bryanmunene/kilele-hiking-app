# Free Deployment Path

This is the recommended free-first hosting setup for Kilele.

## Chosen Stack

```text
Frontend: Streamlit Community Cloud
Backend:  Render Free Web Service
Database: Neon Free Postgres
Images:   Cloudinary Free, optional but recommended for uploads
Domain:   Use the free provider subdomains
```

This avoids paid domains, paid databases, persistent disks, and server management.

## Limits To Accept

- Render Free services sleep after idle time, so the first backend request can take about a minute.
- Neon Free has a small storage/compute allowance. It is enough for a demo, prototype, and light community use.
- Cloudinary Free is enough for light image uploads, but heavy media traffic can exceed free credits.
- This is staging/demo ready, not a high-traffic production architecture.

## 1. Create Neon Database

1. Sign in at Neon with GitHub.
2. Create a free Postgres project.
3. Copy the pooled or direct connection string.
4. Use it as `DATABASE_URL` for both Render and Streamlit.

The connection string should look like:

```text
postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

## 2. Deploy Backend On Render

1. Sign in to Render with GitHub.
2. Choose **New > Blueprint**.
3. Connect this repository and select `main`.
4. Render will detect `render.yaml`.
5. Provide the prompted value:

```text
DATABASE_URL=<your Neon Postgres connection string>
```

The Blueprint assumes these free subdomains:

```text
Backend:  https://kilele-hiking-api.onrender.com
Frontend: https://kilele-hiking-app.streamlit.app
```

If either name is unavailable and the platform gives you a different URL, update these Render environment variables:

```text
API_BASE_URL=https://<your-actual-render-service>.onrender.com
CORS_ORIGINS=https://<your-actual-streamlit-app>.streamlit.app
```

Optional values:

```text
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REDIRECT_URI=https://<your-streamlit-app>.streamlit.app
```

Render will generate `SECRET_KEY` and `STRAVA_WEBHOOK_VERIFY_TOKEN`.

After deploy, verify:

```text
https://<your-render-service>.onrender.com/health
```

## 3. Deploy Frontend On Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud with GitHub.
2. Create a new app from this repository.
3. Branch: `main`
4. Main file path: `frontend/Home.py`
5. Python version: `3.12`
6. Add secrets:

```toml
DATABASE_URL = "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
API_BASE_URL = "https://<your-render-service>.onrender.com"
ENVIRONMENT = "production"
DEBUG = "False"

# Optional persistent image uploads:
CLOUDINARY_CLOUD_NAME = ""
CLOUDINARY_API_KEY = ""
CLOUDINARY_API_SECRET = ""
```

## 4. Optional Cloudinary Free Setup

Use Cloudinary if users will upload profile pictures or hike images. Without Cloudinary, uploads fall back to local files, which can disappear on free cloud services after restarts or redeploys.

1. Create a free Cloudinary account.
2. Copy `cloud_name`, `api_key`, and `api_secret`.
3. Add them to both Render and Streamlit secrets.

## 5. Smoke Test

After both services are live:

1. Open the Streamlit URL.
2. Register a new account.
3. Save a trail bookmark.
4. Add a review.
5. Refresh and confirm the data persists.
6. Check the backend `/health` endpoint.

## Current Readiness

The codebase is ready for this free staging deployment after secrets are added. It still needs manual live QA for Strava OAuth, M-Pesa, Cloudinary uploads, and admin workflows.
