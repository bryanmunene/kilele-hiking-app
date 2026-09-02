# Kilele Hiking

Kilele Hiking is a Python web app for discovering, planning, tracking, reviewing, and organizing Kenyan hiking trails. The repository contains a FastAPI backend and a Streamlit frontend; there is no React Native or Expo app in this codebase.

## Project Structure

```text
backend/    FastAPI API, SQLAlchemy models, SQLite/PostgreSQL configuration
frontend/   Streamlit app, local database service layer, multipage UI
tests/      Contract tests for backend importability and frontend services
```

## Quick Start

### Backend API

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for API documentation.

### Streamlit Frontend

```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed_database.py
streamlit run Home.py --server.port 8501
```

Open `http://localhost:8501`.

## Configuration

Copy `.env.example` to `.env` for local backend settings. For Streamlit secrets, copy `frontend/.streamlit/secrets.toml.example` to `frontend/.streamlit/secrets.toml` and fill in real values locally. The real `secrets.toml` file is intentionally ignored by git.

Strava, Sentry, Cloudinary, email, and wearable imports are optional integrations. The app now starts locally even when optional integration packages or credentials are absent; related features show unavailable/configuration messaging until those dependencies are installed and configured.

## Deployment Readiness

For zero-cost hosting, use the chosen path in [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md): Streamlit Community Cloud, Render Free Web Service, Neon Free Postgres, and optional Cloudinary Free for uploaded images.

The deployable shape is two Python services sharing one persistent PostgreSQL database:

```text
backend   FastAPI service, port 8000 or platform PORT
frontend  Streamlit service, port 8501 or platform PORT
database  PostgreSQL shared by both services
```

For a local production-like run with Docker:

```bash
cp .env.example .env
# Set SECRET_KEY in .env to a unique 32+ character value
docker compose up --build
```

For hosted deployment, configure both services with the same `DATABASE_URL`. Set `ENVIRONMENT=production`, `DEBUG=False`, a strong `SECRET_KEY`, and explicit `CORS_ORIGINS` that include the deployed Streamlit URL. The backend will fail fast if these production guardrails are missing.

Run the readiness checker before deploying:

```bash
python deployment_check.py
```

## Tests

From the repository root:

```bash
python -m compileall backend frontend tests
python -m unittest discover -s tests -v
```

## Admin Access

The seed script no longer creates public default users. Register through the app,
then grant admin privileges explicitly from a trusted environment:

```bash
cd frontend
python make_admin.py your-username-or-email
```

For first-run automation, you can temporarily set `INITIAL_ADMIN_USERNAME`,
`INITIAL_ADMIN_EMAIL`, and `INITIAL_ADMIN_PASSWORD` before running the seed
script, then remove those secrets after the account is created.
