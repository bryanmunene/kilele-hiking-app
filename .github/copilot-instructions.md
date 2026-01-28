# Kilele Hiking App - AI Coding Agent Instructions

## 🎯 Project Overview
Full-stack Kenyan hiking trail application with **dual-database architecture**: FastAPI backend + Streamlit frontend, each with **separate SQLite databases** that sync data.

**Critical Architecture Decision**: Frontend does NOT call backend APIs. Both systems share identical SQLAlchemy models and maintain separate databases that must stay in sync.

## 🏗️ Architecture

### Monorepo Structure
```
Kilele Project/
├── backend/              # FastAPI REST API (unused by frontend)
│   ├── main.py          # FastAPI app entry (port 8000)
│   ├── database.py      # SQLAlchemy config → kilele.db
│   ├── models/          # Shared ORM models (User, Hike, Review, etc.)
│   ├── routers/         # API endpoints (auth, hikes, social, messaging, wearable)
│   └── seed_data.py     # Seeds backend database
│
├── frontend/            # Streamlit multi-page app (port 8501)
│   ├── Home.py          # Main entry point (streamlit run Home.py)
│   ├── database.py      # Separate SQLAlchemy config → frontend/kilele.db
│   ├── models.py        # Duplicate models (MUST match backend)
│   ├── services.py      # Direct DB access layer (replaces API calls)
│   ├── auth.py          # Session-based auth with browser localStorage
│   ├── nature_theme.py  # Reusable CSS theme (greens: #1b5e20, #2e7d32)
│   ├── image_utils.py   # Image display helpers (local/URL handling)
│   ├── seed_database.py # Seeds frontend database
│   └── pages/           # Streamlit pages (numbered 0-18)
```

### Why Two Databases?
- **Backend**: Designed for external API consumers, mobile apps, integrations
- **Frontend**: Streamlit web app accessing its own database for simplicity
- **Trade-off**: Manual sync required when updating models or seeding data
- **Future**: Migrate frontend to call backend APIs OR unify databases

## 🚀 Development Workflow

### Setup (Windows PowerShell)
```powershell
# 1. Activate shared venv (project root)
.venv\Scripts\Activate.ps1

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt
python seed_data.py              # Seeds backend/kilele.db

# 3. Install frontend dependencies
cd ..\frontend
pip install -r requirements.txt
python seed_database.py          # Seeds frontend/kilele.db

# 4. Run backend (optional - not used by frontend)
cd ..\backend
python main.py                   # http://localhost:8000/docs

# 5. Run frontend (primary interface)
cd ..\frontend
streamlit run Home.py            # http://localhost:8501
```

**Environment Files**: Neither backend nor frontend requires `.env` for development (defaults to SQLite)

## 📂 Key Files & Their Roles

### Backend Models (`backend/models/*.py`)
- **Source of truth** for database schema
- When updating: Must duplicate changes to `frontend/models.py`
- Models: `User`, `Hike`, `Review`, `HikeSession`, `Bookmark`, `Achievement`, `Follow`, `Conversation`, `Message`, `SessionToken`, `Activity`
- **Model Sync Warning**: Backend uses `sqlalchemy.sql.func.now()` for defaults; Frontend uses `datetime.utcnow()` - both work but syntax differs
- Backend User has `Activity` relationship; Frontend User has additional `is_admin` and `bio` fields

### Frontend Services (`frontend/services.py`)
- **Replaces API calls** with direct SQLAlchemy queries
- Pattern: `get_all_hikes()` → `db.query(Hike).all()`
- All functions use `with get_db() as db:` context manager
- Returns dictionaries (not ORM objects) for Streamlit compatibility
- **Critical**: Never use `requests.get()` or API calls - always query database directly

### Authentication (`frontend/auth.py`)
- Session tokens stored in `SessionToken` model (30-day expiry, 10 years for "Nesh")
- Browser localStorage via `browser_storage.py` using JavaScript injected via `streamlit.components.html()`
- Pattern: `authenticate_user()` → `create_session_token()` → `save_token_to_browser()`
- Check auth: `if is_authenticated(): user = get_current_user()`
- **Browser Storage Pattern**: Injects JS to read/write `localStorage.kilele_session_token` and uses `postMessage` for Streamlit communication
- **Session Restoration**: `Home.py` calls `restore_session_from_storage()` at startup - this persists login across refreshes
- **Nesh Special Access**: Username "Nesh" is hardcoded as permanent admin with 10-year session tokens

### Browser Storage (`frontend/browser_storage.py`)
- Bridges Streamlit (Python) with browser localStorage (JavaScript)
- Uses `streamlit.components.html()` to inject JS snippets
- Pattern: `window.parent.postMessage({type: 'streamlit:setComponentValue', value: data}, '*')`
- Functions: `save_token_to_browser()`, `load_token_from_browser()`, `clear_token_from_browser()`
- **Height Trick**: All HTML components use `height=0` to avoid visual artifacts

### Streamlit Pages (`frontend/pages/*.py`)
- **Numbered for sidebar order**: `0_🔐_Login.py`, `1_🗺️_Map_View.py`, etc.
- Session restoration handled in `Home.py` - no need to call in every page
- Import pattern:
  ```python
  import sys, os
  sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  from auth import is_authenticated, get_current_user
  from services import get_all_hikes, create_bookmark
  from nature_theme import apply_nature_theme
  ```

### Image Utilities (`frontend/image_utils.py`)
- Handles both local files and URLs for image display
- Pattern: `display_image(hike['image_url'], caption=hike['name'])`
- Automatically checks if image is URL (http) or local file (static/)
- Fallback to emoji (🏔️ 📷) if image missing/fails to load
- `image_exists()` checks file presence before rendering
- All images stored in `frontend/static/` directory

## 🔑 Critical Patterns

### 1. Database Access (Frontend)
```python
from database import get_db
from models import Hike

def get_hike(hike_id: int):
    with get_db() as db:
        hike = db.query(Hike).filter(Hike.id == hike_id).first()
        return {"id": hike.id, "name": hike.name, ...}  # Return dict
```

### 2. Authentication Flow
```python
# Login page
user = authenticate_user(username, password)  # Returns dict
token = create_session_token(user['id'])
st.session_state.authenticated = True
st.session_state.user = user
save_token_to_browser(token)  # Persists across refreshes

# Protected pages
restore_session_from_storage()  # Call at top of every page
if not is_authenticated():
    st.warning("Please login first")
    st.stop()
user = get_current_user()
```

### 3. Nature Theme Application
```python
from nature_theme import apply_nature_theme
st.set_page_config(page_title="...", page_icon="🏔️", layout="wide")
apply_nature_theme()  # Adds CSS with green gradients
```

### 4. Image Display
```python
from image_utils import display_image
display_image(hike['image_url'], caption=hike['name'])
```

### 5. Admin-Only Pages
```python
# Check admin privileges (e.g., 14_👑_Admin_Dashboard.py)
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.stop()

user = get_current_user()
if not user.get('is_admin', False):
    st.error("🚫 Access Denied - Admins only")
    st.stop()

# "Nesh" user has permanent admin access (hardcoded)
```

## 📊 Database Models (Shared Schema)

### Core Models
- **Hike**: Trails (7 Kenyan locations: Mount Kenya, Ngong Hills, etc.)
- **User**: Auth + profiles (bcrypt passwords, 2FA optional, admin flag)
- **Review**: Trail ratings (1-5 stars, photos, difficulty feedback)
- **HikeSession**: Active hike tracking (GPS, distance, duration)
- **Bookmark**: Saved trails per user
- **Achievement**: Badges (unlocked via `UserAchievement` join table)
- **Follow**: Social following (follower_id → following_id)
- **Message/Conversation**: Direct messaging system
- **SessionToken**: Auth tokens (30-day expiry, permanent for "Nesh")
- **Activity**: User activity feed (activity_type: completed_hike, review, achievement; links to user/hike/related_id)

## 🎨 UI/UX Conventions

### Nature Color Palette
- **Primary Green**: `#1b5e20` (dark), `#2e7d32` (medium), `#43a047` (light)
- **Backgrounds**: Soft gradients (`#e8f5e9` → `#f1f8e9` → `#fff8e1`)
- **Sidebar**: Dark green gradient with white text
- **Cards**: White with green accents, subtle shadows

### Streamlit Patterns
- Use `st.columns()` for responsive layouts (mobile-friendly)
- `st.expander()` for detailed trail info
- `st.spinner("Loading...")` for DB operations
- `st.rerun()` after mutations (e.g., creating bookmark)
- `st.session_state` for temporary data (not for auth - use DB tokens)

## ⚠️ Common Pitfalls

### 1. Database Sync Issues
**Problem**: Updating backend models without updating frontend models
**Solution**: Always edit both `backend/models/*.py` AND `frontend/models.py`

### 2. API Calls in Frontend
**Problem**: Adding `requests.get(API_BASE_URL)` in new pages
**Solution**: Use `services.py` functions that query DB directly

### 3. Auth State Loss
**Problem**: User logged out on page refresh
**Solution**: Session is automatically restored via `Home.py` calling `restore_session_from_storage()` - tokens stored in browser localStorage

### 4. Image Paths
**Problem**: Using absolute paths or missing `static/` folder
**Solution**: Use relative URLs (`/static/profiles/user_123.jpg`) and ensure folder exists

## 🧪 Testing & Debugging

### Reset Databases
```powershell
# Frontend (most common)
cd frontend
Remove-Item kilele.db
python seed_database.py
streamlit run Home.py

# Backend
cd backend
Remove-Item kilele.db
python seed_data.py
python main.py
```

### Debug Auth Issues
```python
# Add to any page
st.write("Session State:", st.session_state)
st.write("Auth Status:", is_authenticated())
st.write("Current User:", get_current_user())
```

### Check Database Contents
```powershell
cd frontend
python -c "from database import *; from models import *; init_database(); print('Tables:', Base.metadata.tables.keys())"
```

## 🚢 Deployment Notes

### Streamlit Cloud
1. Push to GitHub
2. Connect repo at share.streamlit.io
3. Set main file: `frontend/Home.py`
4. Secrets: Not required for SQLite (DB auto-created)
5. Dependencies: `frontend/requirements.txt` (includes bcrypt, pyotp, qrcode)

### Backend Deployment (Optional)
- Railway/Render: Use `backend/Procfile`
- PostgreSQL: Update `DATABASE_URL` in `.env`
- CORS: Already configured for `*` origins

## 📝 When Adding Features

### New Database Model
1. Add to `backend/models/` (e.g., `goal.py`)
2. Copy to `frontend/models.py` (with relationships)
3. Create Pydantic schema in `backend/schemas/`
4. Add router in `backend/routers/`
5. Add service functions in `frontend/services.py`
6. Reseed both databases

### New Streamlit Page
1. Create `frontend/pages/N_🎯_PageName.py` (N = sidebar order)
2. Add imports (sys.path, auth, services, theme)
3. Call `restore_session_from_storage()`
4. Apply theme: `apply_nature_theme()`
5. Check auth: `if not is_authenticated(): st.stop()`

### API Endpoint (Backend Only)
- Add to `backend/routers/*.py`
- Use Pydantic schemas for validation
- Access via `Depends(get_db)` dependency injection
- Test at http://localhost:8000/docs

## 🔧 Useful Commands

```powershell
# Find all Streamlit pages
Get-ChildItem frontend\pages -Filter "*.py"

# Search for API calls (should return nothing in services.py)
Select-String -Path frontend\*.py -Pattern "requests\.(get|post)"

# Count database records
python -c "from frontend.database import *; from frontend.models import *; init_database(); print(SessionLocal().query(User).count(), 'users')"

# Make user admin
cd frontend
python make_admin.py  # Prompts for username
```
