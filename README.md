# Kilele Hiking Project

Full-stack hiking trail application for Kenya with Python FastAPI backend and React Native Expo frontend.

## Quick Start

### Backend (Python FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python seed_data.py
python main.py
```
Visit: http://localhost:8000/docs

### Frontend (Streamlit)
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
Visit: http://localhost:8501

## Project Structure

```
Kilele Project/
├── backend/         # Streamlit Python webrver
├── frontend/        # React Native Expo app
└── HikingApp/       # (Legacy - can be removed)
```

## Features

- 7 Kenyan hiking trails (Mount Kenya, Ngong Hills, Karura Forest, etc.)
- RESTful API with SQLite database
- Streamlit web app with filtering and sorting
- Mobile-responsive design
- No JavaScript/npm required - 100% Python!

## Documentation

- **Full Architecture**: See `.github/copilot-instructions.md`
- **Backend API**: See `backend/README.md`
- **API Docs**: http://localhost:8000/docs (when running)

## Development

1. Start backend: `cd backend && pystreamlit run app.py`
3. Open http://localhost:8501 in your browser

## Tech Stack

- **Backend**: Python 3, FastAPI, SQLAlchemy, SQLite
- **Frontend**: Streamlit, Requests
- **100% Python** - No JavaScript/Node.js required!
- **Frontend**: React Native 0.79, Expo 53, React 19
- **API**: RESTful with automatic OpenAPI docs
