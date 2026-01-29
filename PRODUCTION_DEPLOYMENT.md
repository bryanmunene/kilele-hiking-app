# 🚀 Kilele Production Deployment Guide

Complete guide to deploying Kilele to production with PostgreSQL, Cloudinary, and email services.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup (PostgreSQL)](#database-setup)
3. [Image Storage (Cloudinary)](#image-storage)
4. [Email Service (SendGrid)](#email-service)
5. [Error Tracking (Sentry)](#error-tracking)
6. [Backend Deployment (Railway)](#backend-deployment)
7. [Frontend Deployment (Streamlit Cloud)](#frontend-deployment)
8. [Post-Deployment](#post-deployment)

---

## 📦 Prerequisites

### Required Accounts (All Free Tiers Available)

1. **PostgreSQL Database** - Choose one:
   - [Neon](https://neon.tech) - ✅ Recommended (Free 0.5GB)
   - [Supabase](https://supabase.com) - (Free 500MB)
   - [Railway](https://railway.app) - (Includes PostgreSQL)

2. **Image Storage**:
   - [Cloudinary](https://cloudinary.com) - Free 25GB storage + 25GB bandwidth

3. **Email Service**:
   - [SendGrid](https://sendgrid.com) - Free 100 emails/day

4. **Error Tracking** (Optional):
   - [Sentry](https://sentry.io) - Free 5k errors/month

5. **Hosting**:
   - [Railway](https://railway.app) - Backend API (Free $5/month credit)
   - [Streamlit Cloud](https://streamlit.io/cloud) - Frontend (Free public apps)

---

## 🗄️ Database Setup (PostgreSQL)

### Option A: Neon (Recommended)

1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project: **kilele-production**
3. Copy the connection string:
   ```
   postgresql://username:password@ep-xxx.neon.tech/kilele?sslmode=require
   ```
4. Save this - you'll need it later

### Option B: Supabase

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project: **kilele-production**
3. Go to **Settings → Database**
4. Copy the "Connection string" (URI format)
5. Replace `[YOUR-PASSWORD]` with your actual password

### Option C: Railway (Easiest - includes deployment)

1. Railway provides PostgreSQL with backend deployment
2. See [Backend Deployment](#backend-deployment) section

---

## ☁️ Image Storage (Cloudinary)

1. **Sign up** at [cloudinary.com](https://cloudinary.com)

2. After login, go to **Dashboard**

3. **Copy your credentials**:
   - Cloud Name: `your-cloud-name`
   - API Key: `123456789012345`
   - API Secret: `abcdefghijklmnopqrstuvwxyz`

4. **Create upload presets** (Optional):
   - Go to **Settings → Upload**
   - Create preset for `profiles`, `trails`, `reviews`

---

## 📧 Email Service (SendGrid)

1. **Sign up** at [sendgrid.com](https://sendgrid.com)

2. **Verify sender identity**:
   - Go to **Settings → Sender Authentication**
   - Verify your email (or domain)

3. **Create API key**:
   - Go to **Settings → API Keys**
   - Click "Create API Key"
   - Name: `kilele-production`
   - Permissions: **Full Access** (or Mail Send only)
   - **Copy the key** (you can't view it again!)

4. **Save**:
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## 🔍 Error Tracking (Sentry) - Optional

1. **Sign up** at [sentry.io](https://sentry.io)

2. **Create a project**:
   - Platform: **Python** and **FastAPI**
   - Name: `kilele-backend`

3. **Copy DSN**:
   ```
   https://xxxxxxxxxxxxxxxxxxxxx@o1234567.ingest.sentry.io/9876543
   ```

4. **Repeat for frontend** (if desired):
   - Create another project: `kilele-frontend`
   - Platform: **Python**

---

## 🚂 Backend Deployment (Railway)

### Step 1: Prepare Code

1. **Update requirements** (already done):
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Test locally with PostgreSQL**:
   ```bash
   # Create .env file
   DATABASE_URL=your-postgres-connection-string
   python migrate_to_postgres.py
   python main.py
   ```

### Step 2: Deploy to Railway

1. **Go to** [railway.app](https://railway.app)

2. **Create new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select `Kilele Project` repository

3. **Configure deployment**:
   - Root directory: `backend`
   - Build command: Auto-detected
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add PostgreSQL**:
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway will auto-provision

5. **Set environment variables**:
   Go to **Variables** tab and add:
   
   ```bash
   # Database (auto-set by Railway if you added PostgreSQL)
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   
   # Security
   SECRET_KEY=<generate with: openssl rand -hex 32>
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   
   # SendGrid
   SENDGRID_API_KEY=SG.xxxxxxxx
   FROM_EMAIL=noreply@kilele.app
   
   # Sentry (optional)
   SENTRY_DSN=your-sentry-dsn
   SENTRY_ENVIRONMENT=production
   
   # App config
   ENVIRONMENT=production
   DEBUG=False
   CORS_ORIGINS=https://your-app.streamlit.app,http://localhost:8501
   ```

6. **Deploy**:
   - Railway will auto-deploy on git push
   - Or click "Deploy" manually

7. **Get your API URL**:
   - Go to **Settings** → **Domains**
   - Copy the URL: `https://your-app.railway.app`
   - Save this for frontend configuration

### Step 3: Migrate Data

```powershell
# Set environment variable to production database
$env:DATABASE_URL="your-production-postgresql-url"

# Run migration
python migrate_to_postgres.py
```

---

## 🎨 Frontend Deployment (Streamlit Cloud)

### Step 1: Prepare Code

1. **Update configuration** (already done):
   - `frontend/config.py` reads from Streamlit secrets
   - `frontend/.streamlit/config.toml` has app config
   - `frontend/requirements.txt` has all dependencies

### Step 2: Deploy to Streamlit Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)

2. **Click "New app"**:
   - Repository: Select your GitHub repo
   - Branch: `main` (or your default branch)
   - Main file path: `frontend/Home.py`

3. **Advanced settings** → **Secrets**:
   
   Paste this (replace with your actual values):
   
   ```toml
   # Database (production PostgreSQL)
   DATABASE_URL = "postgresql://user:pass@host:5432/kilele"
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME = "your-cloud-name"
   CLOUDINARY_API_KEY = "your-api-key"
   CLOUDINARY_API_SECRET = "your-api-secret"
   
   # Sentry (optional)
   SENTRY_DSN = "your-sentry-dsn"
   
   # App config
   ENVIRONMENT = "production"
   DEBUG = "False"
   API_BASE_URL = "https://your-backend.railway.app"
   ```

4. **Deploy**:
   - Click "Deploy!"
   - Wait 3-5 minutes for deployment

5. **Get your app URL**:
   - Copy URL: `https://your-app.streamlit.app`
   - Share with users!

### Step 3: Update CORS

Go back to Railway and add your Streamlit URL to CORS:

```bash
CORS_ORIGINS=https://your-app.streamlit.app
```

---

## ✅ Post-Deployment

### 1. Test Core Features

- [ ] **Authentication**: Register, login, logout
- [ ] **Trail Browsing**: View all trails
- [ ] **Image Upload**: Profile picture, trail images
- [ ] **Bookmarks**: Save trails
- [ ] **Reviews**: Add and view reviews
- [ ] **Achievements**: Check if unlocking works
- [ ] **Social**: Follow/unfollow users
- [ ] **Messages**: Send direct messages

### 2. Create Admin Account

1. **Register** a normal account with your email
2. **Run locally** to make it admin:
   ```bash
   cd frontend
   python make_admin.py
   # Enter your username
   ```
3. **Or update directly in database**:
   ```sql
   UPDATE users SET is_admin = true WHERE username = 'your-username';
   ```

### 3. Seed Production Data

1. **Add real Kenyan trails** via Admin Dashboard
2. **Upload high-quality photos** to Cloudinary
3. **Create sample reviews** for each trail
4. **Set up achievements** (already in seed data)

### 4. Set Up Monitoring

**Sentry Dashboard**:
- Check for errors at [sentry.io](https://sentry.io)
- Set up alerts for critical errors

**Railway Metrics**:
- Monitor CPU/Memory usage
- Check API response times

**Streamlit Analytics**:
- Check visitor metrics in Streamlit Cloud dashboard

### 5. Custom Domain (Optional)

**Backend (Railway)**:
1. Go to Settings → Domains
2. Add custom domain (e.g., `api.kilele.app`)
3. Update DNS records as shown

**Frontend (Streamlit Cloud)**:
- Custom domains require Streamlit Pro plan
- Or use Railway/Vercel to host frontend instead

---

## 🔧 Troubleshooting

### Database Connection Errors

```python
# Check connection string format
# Correct: postgresql://user:pass@host:5432/dbname
# Incorrect: postgres://... (missing 'ql')

# If using Supabase, ensure port is 5432
```

### Cloudinary Upload Failures

```python
# Check credentials in environment variables
# Ensure Cloudinary account is verified
# Check file size limits (10MB default)
```

### Email Not Sending

```python
# Verify sender email in SendGrid
# Check API key permissions (Full Access or Mail Send)
# Ensure FROM_EMAIL matches verified sender
```

### CORS Errors

```python
# Update CORS_ORIGINS in backend Railway config
# Include both production URL and localhost (for testing)
CORS_ORIGINS=https://your-app.streamlit.app,http://localhost:8501
```

### Rate Limiting Issues

```python
# Adjust limits in backend/.env:
RATE_LIMIT_LOGIN=10  # Increase if needed
RATE_LIMIT_API=100
RATE_LIMIT_UPLOAD=20
```

---

## 📊 Monitoring Commands

### Check Database Health
```bash
# Connect to production database
psql $DATABASE_URL

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname = 'public';

# Count records
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'hikes', COUNT(*) FROM hikes
UNION ALL
SELECT 'reviews', COUNT(*) FROM reviews;
```

### Test Email Service
```python
# backend/test_email.py
from email_service import email_service

result = email_service.send_welcome_email(
    "your-email@example.com",
    "TestUser"
)
print(f"Email sent: {result}")
```

### Test Cloudinary
```python
# backend/test_cloudinary.py
from cloudinary_service import cloudinary_service

result = cloudinary_service.upload_image(
    "path/to/test-image.jpg",
    folder="kilele/test"
)
print(f"Upload result: {result}")
```

---

## 🎉 Success!

Your Kilele app is now live and production-ready!

**Key Features Enabled**:
- ✅ Scalable PostgreSQL database
- ✅ Cloud image storage (Cloudinary)
- ✅ Email notifications
- ✅ Error tracking (Sentry)
- ✅ Rate limiting & security
- ✅ Mobile-optimized UI
- ✅ Professional deployment

**Share your app**:
- Frontend: `https://your-app.streamlit.app`
- Backend API: `https://your-api.railway.app/docs`

**Next Steps**:
1. Add real trail data with GPS coordinates
2. Upload professional photos
3. Invite beta testers
4. Gather feedback and iterate
5. Consider native mobile app (React Native)

---

## 📞 Support

- **Documentation**: Check other guides in project root
- **Issues**: Create GitHub issue
- **Railway Support**: [docs.railway.app](https://docs.railway.app)
- **Streamlit Support**: [docs.streamlit.io](https://docs.streamlit.io)

**Happy Hiking! 🏔️**
