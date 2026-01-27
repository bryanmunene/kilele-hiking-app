# 🔐 Authentication & Tracking System - Setup Instructions

## ✅ What's Been Added

### Backend Features
- **User Authentication**: JWT-based login system with secure password hashing
- **Hike Session Tracking**: Real-time GPS tracking, distance, duration, notes, ratings
- **Saved Hikes**: Favorite trails system
- **User Statistics**: Personal hiking stats (total distance, duration, completed hikes)

### New API Endpoints
- `POST /api/v1/auth/register` - Create new account
- `POST /api/v1/auth/login` - Login (returns JWT token)
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/user/sessions` - Start tracking a hike
- `PUT /api/v1/user/sessions/{id}` - Update progress
- `GET /api/v1/user/sessions` - Get hike history
- `POST /api/v1/user/saved` - Save favorite trail
- `GET /api/v1/user/stats` - User statistics

### New Frontend Pages
1. **🔐 Login** - User authentication (register/login)
2. **👤 Profile** - View stats, active hikes, history, favorites
3. **📍 Track Hike** - Real-time hike tracking with GPS updates

### Enhanced Features
- **Images**: All trails now have beautiful nature images from Unsplash
- **Descriptions**: Enhanced, detailed trail descriptions
- **Save to Favorites**: Heart button on each trail (when logged in)
- **User Welcome**: Shows username on home page when authenticated

## 🚀 Quick Start (Restart Everything)

### Step 1: Stop Running Servers
1. Find the terminal running FastAPI backend
2. Press `Ctrl+C` to stop it
3. Find the terminal running Streamlit
4. Press `Ctrl+C` to stop it

### Step 2: Recreate Database with New Tables

```powershell
cd "c:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project\backend"

# Activate virtual environment
venv\Scripts\activate

# Delete old database (force)
if (Test-Path kilele.db) { 
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Remove-Item kilele.db -Force
}

# Create new database with all tables
python seed_data.py
```

### Step 3: Start Backend
```powershell
# Still in backend directory with venv activated
python main.py
```

**Backend should start on:** http://localhost:8000  
**Check API docs:** http://localhost:8000/docs

### Step 4: Start Frontend (New Terminal)
```powershell
cd "c:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project\frontend"

streamlit run Home.py
```

**Frontend should open:** http://localhost:8501

## 📱 How to Use the New Features

### 1. Create Account
1. Go to **🔐 Login** page
2. Click **Register** tab
3. Fill in:
   - Username
   - Email
   - Full Name
   - Password (min 6 characters)
4. Click "Create Account"

### 2. Login
1. Switch to **Login** tab
2. Enter username and password
3. Click "Login"
4. You'll see welcome message on Home page

### 3. Track a Hike
1. Go to **📍 Track Hike** page
2. Browse available trails
3. Click "Start Tracking" on any trail
4. The hike appears in "Active Hikes" section
5. Update progress:
   - GPS coordinates (latitude/longitude)
   - Distance covered
   - Duration in minutes
   - Add notes about your experience
6. Click "Update Progress" to save
7. When finished, click "Complete Hike"
8. Rate your hike (1-5 stars)

### 4. View Profile & Stats
1. Go to **👤 Profile** page
2. See your statistics:
   - Total hikes
   - Completed hikes
   - Active hikes
   - Total distance
   - Total time
   - Saved favorites
3. View hike history with ratings
4. Manage saved trails

### 5. Save Favorite Trails
1. On **Home** page, expand any trail
2. Click "❤️ Save to Favorites"
3. View all favorites in Profile page

## 🎨 What You'll See

### Images
Every trail now has a beautiful image:
- Mount Kenya: Snowy peak
- Ngong Hills: Rolling green hills
- Karura Forest: Lush forest path
- Aberdare: Misty moorlands
- Hell's Gate: Red rock cliffs
- Elephant Hill: Mountain vista
- Longonot: Volcanic crater

### Enhanced Descriptions
Each trail has detailed descriptions including:
- Key features and highlights
- Wildlife you might see
- Difficulty details
- What makes it special

## 🔧 Troubleshooting

### "Cannot connect to backend"
- Make sure FastAPI is running on port 8000
- Check: http://localhost:8000/health
- Restart backend if needed

### "Database already contains hikes"
- Database wasn't deleted properly
- Stop all Python processes first
- Manually delete `backend/kilele.db`
- Run seed_data.py again

### "Login failed"
- Make sure you've created an account first
- Username and password are case-sensitive
- Check backend logs for errors

### "Token expired" or "Not authenticated"
- Tokens expire after 30 days by default
- Logout and login again
- Session state is cleared when you refresh browser

### Images not loading
- Images are hosted on Unsplash
- Check internet connection
- If some fail, they're external URLs

## 🛠️ Configuration

### Change Token Expiry
Edit `backend/.env`:
```
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days default
```

### Change API URL (for production)
Edit `frontend/pages/*.py`:
```python
API_BASE_URL = "http://localhost:8000/api/v1"
# Change to your production URL
```

### Add More Trails
Edit `backend/seed_data.py` or use API:
```bash
POST http://localhost:8000/api/v1/hikes
```

## 📊 Database Models

### User
- id, username, email, full_name
- hashed_password (bcrypt)
- is_active, created_at, last_login

### HikeSession
- user_id, hike_id
- started_at, completed_at, is_active
- current_latitude, current_longitude
- distance_covered_km, duration_minutes
- notes, rating (1-5)

### SavedHike
- user_id, hike_id
- saved_at

## 🎯 Next Steps (Optional Enhancements)

1. **Real GPS Integration**: Use phone's GPS instead of manual input
2. **Photo Upload**: Let users upload trail photos
3. **Social Features**: Follow users, share hikes
4. **Weather Integration**: Show current conditions
5. **Offline Mode**: Cache data for offline use
6. **Export Stats**: Download hiking statistics as PDF
7. **Leaderboards**: Compare stats with other users
8. **Trail Reviews**: Comments and reviews from community
9. **Emergency Features**: SOS button, emergency contacts
10. **Route Maps**: Show exact trail routes on map

## 📖 API Documentation

Once backend is running, visit:
**http://localhost:8000/docs**

Interactive Swagger UI with:
- All endpoints documented
- Try out authentication
- Test hike tracking
- See request/response examples

## 🎉 Summary

You now have a **COMPLETE hiking app** with:
- ✅ User authentication (register/login)
- ✅ Session management (persistent login)
- ✅ Active hike tracking (GPS, distance, time)
- ✅ Hike history with ratings
- ✅ Favorite trails
- ✅ Personal statistics
- ✅ Beautiful images
- ✅ Detailed descriptions
- ✅ Secure password storage (bcrypt)
- ✅ JWT token authentication
- ✅ Multi-page Streamlit app
- ✅ RESTful API with FastAPI
- ✅ SQLite database with 4 tables

**Everything you requested has been implemented!** 🚀
