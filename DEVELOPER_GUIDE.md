# 🚀 Kilele Developer Quick Start Guide

## Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git

## Quick Setup

### 1. Clone & Setup Backend

```bash
cd "Kilele Project/backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file (if not exists)
echo DATABASE_URL=sqlite:///./kilele.db > .env
echo API_HOST=0.0.0.0 >> .env
echo API_PORT=8000 >> .env

# Seed database
python seed_data.py
python seed_achievements.py

# Start backend server
python main.py
```

**Backend runs on**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

### 2. Setup Frontend

```bash
cd "Kilele Project/frontend"

# Install dependencies
pip install -r requirements.txt

# Start Streamlit app
streamlit run Home.py
```

**Frontend runs on**: http://localhost:8501

---

## 📁 Project Structure

```
Kilele Project/
├── backend/                    # FastAPI backend
│   ├── main.py                # Application entry point
│   ├── database.py            # SQLAlchemy configuration
│   ├── requirements.txt       # Python dependencies
│   ├── seed_data.py          # Trail data seeding
│   ├── seed_achievements.py  # Achievement data seeding
│   ├── models/               # Database models
│   │   ├── user.py           # User model
│   │   ├── hike.py           # Hike model
│   │   ├── review.py         # Review models
│   │   ├── bookmark.py       # Bookmark model
│   │   ├── follow.py         # Follow model
│   │   ├── achievement.py    # Achievement models
│   │   └── activity.py       # Activity model
│   ├── schemas/              # Pydantic schemas
│   │   ├── user.py           # User schemas
│   │   ├── hike.py           # Hike schemas
│   │   └── social.py         # Social feature schemas
│   └── routers/              # API endpoints
│       ├── auth.py           # Authentication endpoints
│       ├── hikes.py          # Hike endpoints
│       ├── user_activity.py  # User activity endpoints
│       └── social.py         # Social feature endpoints
│
└── frontend/                  # Streamlit frontend
    ├── Home.py               # Homepage
    ├── requirements.txt      # Python dependencies
    └── pages/                # Application pages
        ├── 0_🔐_Login.py     # Login/Register
        ├── 1_🗺️_Map_View.py  # Trail browsing
        ├── 2_➕_Add_Trail.py  # Add new trail
        ├── 3_📊_Analytics.py  # User analytics
        ├── 4_👤_Profile.py    # User profile
        ├── 5_📍_Track_Hike.py # Track hiking
        ├── 6_🔐_2FA_Setup.py  # 2FA configuration
        ├── 7_⭐_Reviews.py    # Trail reviews (NEW)
        ├── 8_🔖_Bookmarks.py  # Bookmarked trails (NEW)
        ├── 9_📰_Feed.py       # Activity feed (NEW)
        ├── 10_🏆_Achievements.py # Achievements (NEW)
        └── 11_👥_Social.py    # Social connections (NEW)
```

---

## 🔑 Key API Endpoints

### Authentication
```
POST /api/v1/auth/register      # Register new user
POST /api/v1/auth/login         # Login
POST /api/v1/auth/upload-profile-picture  # Upload profile pic
POST /api/v1/auth/setup-2fa     # Setup 2FA
POST /api/v1/auth/verify-2fa    # Verify 2FA token
```

### Hikes
```
GET    /api/v1/hikes            # List all hikes
GET    /api/v1/hikes/{id}       # Get specific hike
POST   /api/v1/hikes            # Create new hike
PUT    /api/v1/hikes/{id}       # Update hike
DELETE /api/v1/hikes/{id}       # Delete hike
```

### Reviews (NEW)
```
POST /api/v1/social/reviews                    # Create review
GET  /api/v1/social/reviews/hike/{id}          # Get trail reviews
POST /api/v1/social/reviews/{id}/helpful       # Mark helpful
POST /api/v1/social/reviews/{id}/photos        # Upload photos
```

### Bookmarks (NEW)
```
POST   /api/v1/social/bookmarks     # Create bookmark
GET    /api/v1/social/bookmarks     # Get user bookmarks
DELETE /api/v1/social/bookmarks/{id} # Remove bookmark
```

### Social (NEW)
```
POST   /api/v1/social/follow        # Follow user
DELETE /api/v1/social/follow/{id}   # Unfollow user
GET    /api/v1/social/followers     # Get followers
GET    /api/v1/social/following     # Get following
GET    /api/v1/social/feed          # Get activity feed
```

### Achievements (NEW)
```
GET /api/v1/social/achievements     # Get user achievements
```

### Statistics (NEW)
```
GET /api/v1/social/statistics       # Get user statistics
```

---

## 🗄️ Database Models

### User
- id, username, email, hashed_password
- full_name, created_at
- profile_picture, two_fa_enabled, two_fa_secret
- Relationships: reviews, bookmarks, achievements, activities

### Hike
- id, name, location, difficulty
- distance_km, elevation_gain_m, estimated_duration_hours
- description, trail_type, best_season
- latitude, longitude, image_url
- Relationships: reviews, bookmarks

### Review (NEW)
- id, user_id, hike_id
- rating (1-5), title, comment
- difficulty_rating (1-5), conditions, visited_date
- helpful_count

### Bookmark (NEW)
- id, user_id, hike_id
- notes (personal notes)

### Follow (NEW)
- id, follower_id, following_id

### Achievement (NEW)
- id, name, description, icon
- category, requirement, points

### UserAchievement (NEW)
- id, user_id, achievement_id
- earned_at, progress, completed

### Activity (NEW)
- id, user_id, activity_type
- hike_id, related_id, description

---

## 🛠️ Development Commands

### Backend

```bash
# Run server with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Reset database
rm kilele.db
python seed_data.py
python seed_achievements.py

# View logs
# Server logs appear in terminal

# Test API
# Open http://localhost:8000/docs
```

### Frontend

```bash
# Run Streamlit app
streamlit run Home.py

# Run on specific port
streamlit run Home.py --server.port 8502

# Clear cache
# In browser: Press 'C' then 'Enter'

# Stop server
# Press Ctrl+C in terminal
```

---

## 🧪 Testing the New Features

### 1. Test Reviews
1. Login to the app
2. Go to ⭐ Reviews page
3. Select "Write Review" tab
4. Choose a trail
5. Fill in rating, conditions, and review
6. Submit
7. Go to "Browse Reviews" tab to see your review

### 2. Test Bookmarks
1. Go to 🔖 Bookmarks page
2. Click "Add Bookmark" tab
3. Select a trail
4. Add optional notes
5. Bookmark the trail
6. View in "My Bookmarks" tab

### 3. Test Social Features
1. Create a second user account (use different browser/incognito)
2. Go to 👥 Social page
3. Follow the other user
4. Complete a hike or write a review
5. Check the other user's 📰 Feed page
6. You should see your activity

### 4. Test Achievements
1. Go to 🏆 Achievements page
2. View locked achievements
3. Complete a hike (Track Hike page)
4. Write a review
5. Return to achievements page
6. Check if "First Steps" or "Critic's Choice" unlocked

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill process using port 8000
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # macOS/Linux
```

### Frontend can't connect to backend
- Verify backend is running on http://localhost:8000
- Check API_BASE_URL in frontend pages
- Try accessing http://localhost:8000/docs directly

### Database errors
```bash
# Delete and recreate database
rm kilele.db
python seed_data.py
python seed_achievements.py
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📦 Dependencies

### Backend (requirements.txt)
```
fastapi==0.115.0
uvicorn[standard]==0.28.0
sqlalchemy==2.0.35
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.22
python-dotenv==1.0.1
bcrypt==4.0.1
pyotp==2.9.0
qrcode[pil]==8.2
pillow==12.1.0
```

### Frontend (requirements.txt)
```
streamlit==1.41.1
requests==2.32.3
plotly==6.0.0
pandas==2.2.3
```

---

## 🔐 Environment Variables

### Backend `.env`
```env
DATABASE_URL=sqlite:///./kilele.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend
No environment variables needed (uses localhost by default)

For production, update `API_BASE_URL` in each page file.

---

## 🚢 Production Deployment

### Backend
1. Set `DEBUG=False` in .env
2. Use PostgreSQL instead of SQLite
3. Set secure `SECRET_KEY`
4. Use gunicorn or similar WSGI server
5. Enable HTTPS
6. Configure CORS properly

### Frontend
1. Deploy to Streamlit Cloud (free)
2. Or use Docker/Heroku
3. Update API_BASE_URL to production backend
4. Configure secrets in deployment platform

---

## 📖 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pydantic Docs**: https://docs.pydantic.dev/

---

## 💡 Pro Tips

1. **Use API Docs**: http://localhost:8000/docs is your friend for testing endpoints
2. **Clear Cache**: Press 'C' in Streamlit to clear cache when data changes
3. **Check Logs**: Both servers print helpful logs in terminal
4. **Use Incognito**: For testing multi-user features, use incognito mode
5. **Database Browser**: Use DB Browser for SQLite to view database directly

---

## 🎯 Next Steps for Development

1. **Add Weather Integration**
   - Sign up for OpenWeatherMap API
   - Create weather service in backend
   - Display on trail details page

2. **Implement Photo Uploads for Reviews**
   - Update review endpoint to handle files
   - Store in static/review_photos/
   - Display in review cards

3. **Add Search Functionality**
   - Create search endpoint with filters
   - Add search bar to Map View page
   - Implement multi-field search

4. **Build Leaderboards**
   - Create leaderboard endpoint
   - Calculate rankings by various metrics
   - Display in new Leaderboards page

5. **Notifications System**
   - Add notifications model
   - Create endpoints for notifications
   - Display in header/sidebar

---

*Happy Hiking! 🏔️*
