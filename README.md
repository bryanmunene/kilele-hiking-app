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

## Tests

From the repository root:

```bash
python -m compileall backend frontend tests
python -m unittest discover -s tests -v
```

## Default Seed Users

The Streamlit seed script creates:

```text
admin / admin123
Nesh / password123
demo / demo123
```
