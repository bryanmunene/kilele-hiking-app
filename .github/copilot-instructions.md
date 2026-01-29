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
│   ├── models/          # Modular ORM models (user.py, hike.py, review.py, etc.)
│   ├── routers/         # API endpoints (auth, hikes, social, messaging, wearable, user_activity)
│   ├── schemas/         # Pydantic validation schemas
│   └── seed_data.py     # Seeds backend database
│
├── frontend/            # Streamlit multi-page app (port 8501)
│   ├── Home.py          # Main entry point (streamlit run Home.py)
│   ├── database.py      # Separate SQLAlchemy config → frontend/kilele.db
│   ├── models.py        # Monolithic models file (MUST match backend)
│   ├── services.py      # Direct DB access layer (replaces API calls)
│   ├── auth.py          # Session-based auth with browser localStorage
│   ├── browser_storage.py # JS bridge for localStorage persistence
│   ├── nature_theme.py  # Reusable CSS theme (blues: #1e3a5f, #2c4563, #4a6fa5)
│   ├── image_utils.py   # Image display helpers (local/URL handling)
│   ├── seed_database.py # Seeds frontend database
│   └── pages/           # Streamlit pages (numbered 0-18: Login → Trail Info)
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
- **Modular structure**: Each model in its own file (user.py, hike.py, review.py, achievement.py, activity.py, bookmark.py, follow.py, hike_session.py, message.py)
- **Source of truth** for database schema
- When updating: Must duplicate changes to `frontend/models.py` (monolithic file)
- Models: `User`, `Hike`, `Review`, `HikeSession`, `Bookmark`, `Achievement`, `Follow`, `Conversation`, `Message`, `SessionToken`, `TrailComment`, `Goal`, `EmergencyContact`, `TrailCondition`, `Equipment`

### Frontend Models (`frontend/models.py`)
- **Monolithic file** containing ALL models in one place
- **Critical**: Must manually sync with backend whenever backend models change
- Includes additional frontend-only fields: `User.is_admin`, `User.bio`
- All relationships defined using string references (e.g., `"Review"`, `"Hike"`)

### Frontend Services (`frontend/services.py`)
- **Replaces API calls** with direct SQLAlchemy queries
- Pattern: `get_all_hikes()` → `db.query(Hike).all()`
- All functions use `with get_db() as db:` context manager
- Returns dictionaries (not ORM objects) for Streamlit compatibility
- **Critical**: Never use `requests.get()` or API calls - always query database directly
- Example functions: `get_all_hikes()`, `create_bookmark()`, `get_user_goals()`, `add_trail_comment()`

### Authentication (`frontend/auth.py`)
- Session tokens stored in `SessionToken` model (30-day expiry, 10 years for "Nesh")
- Browser localStorage via `browser_storage.py` using JavaScript injection
- Pattern: `authenticate_user()` → `create_session_token()` → `save_token_to_browser()`
- Check auth: `if is_authenticated(): user = get_current_user()`
- **Session Restoration**: `Home.py` calls `restore_session_from_storage()` at startup - persists login across refreshes
- **Nesh Special Access**: Username "Nesh" is hardcoded as permanent admin with 10-year session tokens

### Browser Storage (`frontend/browser_storage.py`)
- Bridges Streamlit (Python) with browser localStorage (JavaScript)
- Uses `streamlit.components.html()` to inject JS snippets
- Pattern: `window.parent.postMessage({type: 'streamlit:setComponentValue', value: data}, '*')`
- Functions: `save_token_to_browser()`, `load_token_from_browser()`, `clear_token_from_browser()`
- **Height Trick**: All HTML components use `height=0` to avoid visual artifacts

### Streamlit Pages (`frontend/pages/*.py`)
- **Numbered for sidebar order**: 
  - `0_🔐_Login.py` - Authentication
  - `1_🗺️_Map_View.py` - Trail map with Folium
  - `2_➕_Add_Trail.py` - Admin trail creation
  - `3_📊_Analytics.py` - User statistics
  - `4_👤_Profile.py` - User profiles
  - `5_📍_Track_Hike.py` - Live GPS tracking
  - `6_🔐_2FA_Setup.py` - Two-factor authentication
  - `7_⭐_Reviews.py` - Trail reviews
  - `8_🔖_Bookmarks.py` - Saved trails
  - `9_📰_Feed.py` - Activity feed
  - `10_🏆_Achievements.py` - Badges & milestones
  - `11_👥_Social.py` - Follow system
  - `12_💬_Messages.py` - Direct messaging
  - `13_⌚_Wearables.py` - Garmin/Fitbit integration
  - `14_👑_Admin_Dashboard.py` - Admin panel
  - `15_🎯_Goals.py` - Personal hiking goals
  - `16_🚨_Emergency_Contacts.py` - Safety contacts
  - `17_💬_Trail_Community.py` - Trail discussions
  - `18_🌤️_Trail_Info.py` - Trail conditions
- Session restoration handled in `Home.py` - no need to call in every page
- Import pattern:
  ```python
  import sys, os
  sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  from auth import is_authenticated, get_current_user, restore_session_from_storage
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

### 6. Model Synchronization Pattern
```python
# When adding a new model to backend:
# 1. Create backend/models/new_model.py
class NewModel(Base):
    __tablename__ = "new_models"
    # ... fields ...

# 2. Copy ENTIRE model to frontend/models.py (bottom of file)
# 3. Update relationships using string references (e.g., "User", "Hike")
# 4. Add to both seed scripts (backend/seed_data.py, frontend/seed_database.py)
# 5. Reset both databases:
#    cd backend && Remove-Item kilele.db && python seed_data.py
#    cd frontend && Remove-Item kilele.db && python seed_database.py
```

## 📊 Database Models (Shared Schema)

### Core Models
- **Hike**: Trails (7 Kenyan locations: Mount Kenya, Ngong Hills, Karura Forest, Hell's Gate, Longonot, Aberdare Ranges, Chyulu Hills)
- **User**: Auth + profiles (bcrypt passwords, 2FA optional, admin flag, bio, experience level)
- **Review**: Trail ratings (1-5 stars, photos, difficulty feedback, trail conditions)
- **HikeSession**: Active hike tracking (GPS routes, distance, duration, status: in_progress/completed/paused)
- **Bookmark**: Saved trails per user (created_at timestamp)
- **Achievement**: Badges (name, description, icon, criteria, unlocked via `UserAchievement` join table)
- **Follow**: Social following (follower_id → following_id, created_at)
- **Message/Conversation**: Direct messaging system with participants (ConversationParticipant join table)
- **SessionToken**: Auth tokens (30-day expiry, permanent for "Nesh", stores token hash)

### New Feature Models (Added Jan 2026)
- **TrailComment**: Discussion forums per trail (parent_id for threaded replies, user_id, hike_id)
- **Goal**: Personal hiking goals (goal_type: hikes_completed/distance/elevation/trails_visited, target_value, current_progress, deadline, is_completed)
- **EmergencyContact**: Safety contacts (name, phone, email, relationship, is_primary)
- **TrailCondition**: Real-time trail status (weather, difficulty_level: easy/moderate/hard/closed, crowd_level, condition: excellent/good/fair/poor, safety_notes, reported_by user_id)
- **Equipment**: Gear checklist (name, category: clothing/footwear/safety/navigation/food/camping, is_required, description)

### Relationships & Join Tables
- **UserAchievement**: Links users to unlocked achievements (user_id, achievement_id, unlocked_at)
- **ConversationParticipant**: Links users to conversations (conversation_id, user_id)
- All models use SQLAlchemy relationships with `back_populates` for bidirectional access
- Cascade deletes on parent objects (e.g., deleting Hike removes Reviews, Sessions, Bookmarks)

## 🎨 UI/UX Conventions

### Nature Color Palette
- **Primary Navy Blue**: `#1e3a5f` (dark), `#2c4563` (medium), `#4a6fa5` (compass blue)
- **Mountain Blues**: `#5b7ea8` (light), `#64b5f6` (sky), `#90caf9` (lighter sky)
- **Backgrounds**: Sky blue gradients (`#e3f2fd` → `#bbdefb` → `#90caf9` → `#64b5f6`)
- **Sidebar**: Deep navy gradient with white text
- **Cards**: White with blue accents, subtle shadows

### Streamlit Patterns
- Use `st.columns()` for responsive layouts (mobile-friendly)
- `st.expander()` for detailed trail info
- `st.spinner("Loading...")` for DB operations
- `st.rerun()` after mutations (e.g., creating bookmark)
- `st.session_state` for temporary data (not for auth - use DB tokens)

### Mobile Responsiveness
- **All pages include responsive CSS** via `nature_theme.py`
- **Touch targets**: Minimum 44x44px for buttons/links (Apple HIG standard)
- **Columns**: Automatically stack vertically on mobile (< 768px)
- **Images**: Use `use_column_width=True` by default for responsive sizing
- **Font sizes**: 16px minimum on inputs (prevents iOS zoom)
- **Media queries**: Mobile (< 768px), Tablet (768-1024px), Desktop (> 1024px)
- **When adding pages**: Include mobile CSS override:
  ```python
  st.markdown(\"\"\"
      <style>
      @media (max-width: 768px) {
          [data-testid=\"column\"] {
              width: 100% !important;
              min-width: 100% !important;
          }
      }
      </style>
  \"\"\", unsafe_allow_html=True)
  ```

## ⚠️ Common Pitfalls

### 1. Database Sync Issues
**Problem**: Updating backend models without updating frontend models  
**Solution**: Always edit both `backend/models/*.py` AND `frontend/models.py`. Backend uses modular files; frontend uses single monolithic file.

### 2. API Calls in Frontend
**Problem**: Adding `requests.get(API_BASE_URL)` in new pages  
**Solution**: Use `services.py` functions that query DB directly. Pattern: `from services import get_all_hikes` → `hikes = get_all_hikes()`

### 3. Auth State Loss on Refresh
**Problem**: User logged out on page refresh  
**Solution**: Session is automatically restored via `Home.py` calling `restore_session_from_storage()` - tokens stored in browser localStorage. Do NOT call in individual pages.

### 4. Image Paths
**Problem**: Using absolute paths or missing `static/` folder  
**Solution**: Use relative URLs (`/static/profiles/user_123.jpg`) and ensure folder exists. Use `image_utils.display_image()` for automatic fallback.

### 5. Import Errors in Pages
**Problem**: `ModuleNotFoundError` when importing from parent directory  
**Solution**: Add sys.path manipulation at top of every page:
```python
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### 6. Missing Context Manager for DB
**Problem**: Database connections not closing properly  
**Solution**: Always use `with get_db() as db:` context manager in services.py. Never use `db = SessionLocal()` directly.

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

# Check browser localStorage
# Open browser DevTools → Console → localStorage.getItem('kilele_session_token')
```

### Check Database Contents
```powershell
# List all tables
cd frontend
python -c "from database import *; from models import *; init_database(); print('Tables:', Base.metadata.tables.keys())"

# Count records
python -c "from database import *; from models import *; init_database(); print(SessionLocal().query(User).count(), 'users')"

# Verify model sync
# Backend: Get-Content backend/models/user.py
# Frontend: Get-Content frontend/models.py | Select-String "class User"
```

### Common Streamlit Debugging
- **Page not updating**: Use `st.rerun()` after mutations
- **Session state lost**: Check `st.session_state` keys - auth uses `authenticated`, `user`, `token`
- **Slow queries**: Enable SQL echo in `frontend/database.py` → `echo=True`
- **Import errors**: Verify `sys.path.append()` is first import in page files

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
cd frontend
python -c "from database import *; from models import *; init_database(); print(SessionLocal().query(User).count(), 'users')"

# Make user admin
cd frontend
python make_admin.py  # Prompts for username

# Check model differences (backend vs frontend)
diff (Get-Content backend/models/user.py) (Get-Content frontend/models.py | Select-String "class User" -Context 20)

# Verify all routers loaded
cd backend
python -c "from main import app; print([route.path for route in app.routes])"

# Test authentication flow
cd frontend
python -c "from auth import authenticate_user; print(authenticate_user('testuser', 'password123'))"
```
