# Kilele Project - Hiking App

## Project Overview
Full-stack application for discovering and exploring hiking trails in Kenya. Built with **Python FastAPI backend** and **React Native Expo frontend** in a monorepo structure.

## Architecture

### Monorepo Structure
```
Kilele Project/
├── backend/              # Python FastAPI server
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # SQLAlchemy configuration
│   ├── requirements.txt # Python dependencies
│   ├── seed_data.py     # Database seeding
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic validation schemas
│   └── routers/         # API route handlers
│
└── frontend/            # Streamlit web app
    ├── app.py           # Main Streamlit application
    ├── requirements.txt # Python dependencies (streamlit, requests)
    └── README.md        # Frontend documentation
```

### Tech Stack

**Backend**:
- Python 3.x with FastAPI
- SQLAlchemy ORM
- SQLite (dev) / PostgreSQL (production)
- Uvicorn ASGI server
- Pydantic for data validation

**Frontend**:
- Streamlit (Python web framework)
- Requests library for API calls
- Pure Python - no JavaScript/npm required
- Mobile-responsive design

## Development Workflow

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env

# Seed database with Kenyan trails
python seed_data.py

# Run server (auto-reload enabled)
python main.py
# Or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs on**: http://localhost:8000
**API Docs**: http://localhost:8000/docs (Swagger UI)

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Expo development server
npm start
pip install -r requirements.txt

# Run Streamlit app (auto-opens in browser)
streamlit run app.py
```

**Frontend runs on**: http://localhost:8501
Terminal 1 (Backend):
```bash
cd backend
venv\Scripts\activate
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

## API Endpoints
streamlit run app.py
### Hikes API (`/api/v1/hikes`)

- `GET /api/v1/hikes` - List all hikes
  - Query params: `?difficulty=Moderate&skip=0&limit=100`
- `GET /api/v1/hikes/{id}` - Get specific hike
- `POST /api/v1/hikes` - Create new hike (JSON body)
- `PUT /api/v1/hikes/{id}` - Update hike
- `DELETE /api/v1/hikes/{id}` - Delete hike

### Health Check
- `GET /health` - Server health status

## Data Models

### Hike Model (Database)
```python
{
    "id": int,
    "name": str,                      # e.g., "Mount Kenya Trek"
    "location": str,                  # e.g., "Mount Kenya National Park"
    "difficulty": str,                # Easy, Moderate, Hard, Extreme
    "distance_km": float,
    "elevation_gain_m": float,
    "estimated_duration_hours": float,
    "description": str,
    "trail_type": str,                # Loop, Out and Back, Point to Point
    "best_season": str,
    "latitude": float,
    "longitude": float,
    "image_url": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

## Code Conventions

### Backend (Python)
- **PEP 8** style guide
- FastAPI route functions in `routers/`
- SQLAlchemy models in `models/`
- Pydantic schemas in `schemas/` (request/response validation)
- Use type hints for all function parameters and returns
- Async/await not required (SQLAlchemy is synchronous)

### Frontend (React Native)
- Functional components with hooks
- StyleSheet API for all styles (no inline styles)
- API calls in `services/` layer (separation of concerns)
- Loading and Streamlit/Python)
- **PEP 8** style guide
- Pure Python - no JavaScript required
- Streamlit components for UI (`st.title`, `st.button`, etc.)
- `requests` library for API calls
- Error handling with try/except and `st.error()`
- Caching with `@st.cache_data` for expensive operations
- Use `st.rerun()` to refresh data

### API Integration Pattern
```python
# Fetch data from backend
def fetch_hikes(difficulty=None):
    try:
        params = {'difficulty': difficulty} if difficulty else {}
        response = requests.get(f"{API_BASE_URL}/hikes", params=params)
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return []
### Backend Environment (`.env`)
```bash
DATABASE_URL=sqlite:///./kilele.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Frontend API Config (`app.py`)
```python
# In app.py
API_BASE_URL = "http://localhost:8000/api/v1"  # Development

# For production, use environment variable:
# API_BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
```

## Development Roadmap

### Phase 1: Current Features ✅
- [x] FastAPI backend with RESTful API
- [x] SQLite database with 7 Kenyan trails seeded
- [x] React Native frontend with API integration
- [x] Streamlit web frontend with API integration
- [x] Filtering by difficulty level
- [x] Sorting by name, distance, duration, difficulty
- [x] Loading states and error handling
- [x] Mobile-responsive design
- [x] Expandable detail cards
### PhImage upload and display
- [ ] Multi-page Streamlit app (separate pages for add/edit)
- [ ] Search functionality with text input
- [ ] Map visualization (folium integration)
- [ ] Export trails to CSV/PDFlty/distance
- [ ] Search functionality

### Phase 3: User Features
- [ ] User authentication (JWT tokens)
- [ ] User profiles and saved hikes
- [ ] Trail reviews and ratings
- [ ] Photo galleries per trail
- [ ] Social features (share hikes, follow users)

### Phase 4: Advanced
- [ ] GPS tracking and location services
- [ ] Interactive maps (Google Maps/Mapbox)
- [ ] Offline mode with cached data
- [ ] Weather API integration
- [ ] Emergency contacts and safety features

## Deployment

### Backend Deployment
**Options**: Railway, Render, DigitalOcean, Heroku

**Steps**:
1. Migrate to PostgreSQL for production
2. Set environment variables
3. Deploy via Git or Docker
4. Run database migrations and seeding

**Example (Railway)**:
```bash
railway login
railway init
railway up
```


**Streamlit Cloud (Easiest - Free)**:
```bash
# Push to GitHub, then:
# 1. Go to https://share.streamlit.io
# 2. Connect your GitHub repo
# 3. Select frontend/app.py as main file
# 4. Deploy!
```

**Other Options**:
- Heroku: `heroku create && git push heroku main`
- Railway: `railway up`
- Docker: Create Dockerfile with streamlit
- Any Python hosting platform build --platform android --profile production
```

## Testing

### Backend Testing
```bash
cd backend
pip install pytest pytest-cov
pytest
```
Cannot connect to backend" Error
- ✅ Check backend is running on port 8000
- ✅ Verify `API_BASE_URL` in `app.py` is correct
- ✅ Test backend directly: http://localhost:8000/docs
## Common Issues

### "Failed to load hikes" Error
- ✅ Check backend is running on port 8000
- ✅ Check `config/api.js` has correct URL
- ✅ Android emulator: use `10.0.2.2` not `localhost`
- ✅ Physical device: use computer's local IP

### CORS Errors
- Backend already configured for `allow_origins=["*"]`
- In production, restrict to specific domains

### Database Changes
```bash
# Reset database
cd backend
rm kilele.db
python seed_data.py
```

## Performance Best Practices

### Backend
- Use `@st.cache_data` for API calls that don't change often
- Implement pagination for large datasets
- Use `st.spinner()` for loading states
- Debounce search inputs with session state for PostgreSQL

### Frontend
- Use FlatList instead of ScrollView for long lists
- Implement pagination when dataset grows
- Cache images with Expo Image
- Debounce search inputs

## When Adding Features

### Backend
- Create Pydantic schemas in `schemas/` for validation
- Use `requests.get()` for API calls
- Handle errors with try/except and `st.error()`
- Use Streamlit components (`st.metric`, `st.expander`, etc.)
- Maintain nature-themed color palette in custom CSS
- Use `st.columns()` for responsive layouts
- Add filters in sidebar with `st.sidebar`
### Frontend
- Add API functions to `services/`
- Handle loading, success, and error states
- Use FlatList with `keyExtractor` for lists
- Follow existing shadow/elevation pattern for cards
- Maintain nature-themed color palette (greens: #2e7d32, #1b5e20)

### Database Migrations (Future)
```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```
