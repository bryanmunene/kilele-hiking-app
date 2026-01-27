# Kilele Hiking App - Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Railway (Recommended - Easiest)

#### Backend Deployment (Railway)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend**
   ```bash
   # Install Railway CLI (optional)
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   cd backend
   railway init
   
   # Add PostgreSQL
   railway add postgresql
   
   # Deploy
   railway up
   ```

3. **Configure Environment Variables** (in Railway dashboard):
   ```
   DATABASE_URL=<automatically set by Railway PostgreSQL>
   SECRET_KEY=your-secret-key-here-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Get Backend URL**
   - Railway will provide a URL like: `https://yourapp.railway.app`

#### Frontend Deployment (Streamlit Cloud)

1. **Push to GitHub**
   ```bash
   cd "Kilele Project"
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/kilele-app.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repo
   - Main file path: `frontend/Home.py`
   - Python version: 3.12

3. **Configure Secrets** (in Streamlit Cloud):
   - Go to App Settings → Secrets
   - Add:
   ```toml
   API_BASE_URL = "https://your-backend-url.railway.app/api/v1"
   ```

4. **Update API_BASE_URL in frontend files**
   - Edit `frontend/Home.py` and all page files
   - Change: `API_BASE_URL = "http://localhost:8000/api/v1"`
   - To: `API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")`

---

### Option 2: Render (Alternative)

#### Backend on Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL Database**
   - Dashboard → "New +" → "PostgreSQL"
   - Copy the Internal Database URL

4. **Environment Variables**
   ```
   DATABASE_URL=<from Render PostgreSQL>
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

#### Frontend on Render

1. **Create New Web Service**
   - Root Directory: `frontend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run Home.py --server.port $PORT --server.address 0.0.0.0`

2. **Environment Variables**
   ```
   API_BASE_URL=https://your-backend.onrender.com/api/v1
   ```

---

### Option 3: Heroku

#### Backend

```bash
cd backend
heroku create kilele-backend
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

#### Frontend

```bash
cd frontend
heroku create kilele-frontend
heroku config:set API_BASE_URL=https://kilele-backend.herokuapp.com/api/v1
git push heroku main
```

---

## 📝 Pre-Deployment Checklist

### Backend Changes Needed

1. **Update database.py for PostgreSQL**
   - SQLite → PostgreSQL connection string
   - Handled automatically if using `DATABASE_URL` env var

2. **Update main.py CORS settings**
   - Add your frontend domain to `allow_origins`

3. **Set strong SECRET_KEY**
   - Generate: `openssl rand -hex 32`

4. **Create .env.production**
   ```env
   DATABASE_URL=postgresql://...
   SECRET_KEY=<generated-key>
   ALLOWED_ORIGINS=https://your-frontend.streamlit.app
   ```

### Frontend Changes Needed

1. **Update API_BASE_URL** in all files:
   - `frontend/Home.py`
   - `frontend/pages/*.py`
   
   Change to:
   ```python
   API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")
   ```

2. **Add .streamlit/secrets.toml**
   ```toml
   API_BASE_URL = "https://your-backend-url/api/v1"
   ```

---

## 🗄️ Database Migration (SQLite → PostgreSQL)

### Automatic (Recommended)

Railway and Render handle this automatically when you:
1. Add PostgreSQL addon
2. Set `DATABASE_URL` environment variable
3. Run `python seed_data.py` in production

### Manual Migration

```bash
# Export SQLite data
sqlite3 kilele.db .dump > dump.sql

# Import to PostgreSQL
psql $DATABASE_URL < dump.sql

# Or use pgloader
pgloader kilele.db postgresql://user:pass@host/db
```

---

## 🔒 Security Checklist

- ✅ Change `SECRET_KEY` to a strong random value
- ✅ Set `DEBUG=False` in production
- ✅ Update CORS `allow_origins` to specific domains
- ✅ Use HTTPS for all endpoints
- ✅ Set up proper database backups
- ✅ Enable rate limiting (optional)
- ✅ Review `.env` - never commit secrets to git

---

## 📊 Post-Deployment

1. **Test All Features**
   - User registration/login
   - 2FA setup
   - Profile picture upload
   - Trail browsing/reviews
   - Messages
   - Wearable device import

2. **Seed Production Database**
   ```bash
   # SSH into backend server or use Railway/Render dashboard
   python seed_data.py
   ```

3. **Monitor Logs**
   - Railway: `railway logs`
   - Render: View logs in dashboard
   - Streamlit: Check app logs in settings

4. **Set up Custom Domain** (Optional)
   - Railway: Settings → Domains
   - Streamlit Cloud: Settings → Custom domain

---

## 🆘 Troubleshooting

### Backend Issues

**Database Connection Error:**
- Check `DATABASE_URL` format: `postgresql://user:pass@host:5432/dbname`
- Ensure PostgreSQL addon is created
- Run migrations: `python seed_data.py`

**Static Files Not Loading:**
- Check CORS settings in `main.py`
- Verify static directory exists in deployment

### Frontend Issues

**Can't Connect to Backend:**
- Verify `API_BASE_URL` in secrets
- Check backend CORS allows frontend domain
- Ensure backend is deployed and running

**Import Errors:**
- Run `pip install -r requirements.txt`
- Check Python version matches

---

## 📈 Scaling Considerations

- **Backend**: Railway/Render auto-scale based on traffic
- **Database**: Upgrade PostgreSQL plan as needed
- **Frontend**: Streamlit Cloud has usage limits (check plan)
- **File Storage**: Consider AWS S3 for profile pictures in production

---

## 💰 Cost Estimates

### Free Tier (Sufficient for MVP)
- **Railway**: $5 credit/month (PostgreSQL + backend)
- **Streamlit Cloud**: Free for public apps
- **Total**: ~$0-5/month

### Paid (Production-Ready)
- **Railway**: ~$20/month (backend + DB)
- **Streamlit Cloud**: $200/month (private apps)
- **Custom Domain**: ~$12/year
- **Total**: ~$220/month

---

## 🎯 Recommended Deployment Path

For fastest deployment:

1. ✅ **Backend**: Railway (5 minutes)
   - Automatic PostgreSQL
   - Simple git push deployment
   - Free $5 credit

2. ✅ **Frontend**: Streamlit Cloud (3 minutes)
   - Direct GitHub integration
   - Free for public apps
   - Automatic redeployment on push

**Total Setup Time**: ~10 minutes 🚀
