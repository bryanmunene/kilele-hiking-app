# 🚀 Kilele Deployment Checklist

Use this checklist to track your deployment progress.

## Phase 1: Account Setup (15 minutes)

### PostgreSQL Database
- [ ] Sign up at [Neon](https://neon.tech) or [Supabase](https://supabase.com)
- [ ] Create project: `kilele-production`
- [ ] Copy connection string
- [ ] Save in password manager

### Cloudinary (Image Storage)
- [ ] Sign up at [cloudinary.com](https://cloudinary.com)
- [ ] Copy Cloud Name
- [ ] Copy API Key
- [ ] Copy API Secret
- [ ] Save credentials

### SendGrid (Email)
- [ ] Sign up at [sendgrid.com](https://sendgrid.com)
- [ ] Verify sender email
- [ ] Create API key (Full Access)
- [ ] Save API key (can't view again!)

### Sentry (Optional - Error Tracking)
- [ ] Sign up at [sentry.io](https://sentry.io)
- [ ] Create project: `kilele-backend`
- [ ] Copy DSN
- [ ] Create project: `kilele-frontend` (optional)

### Railway (Backend Hosting)
- [ ] Sign up at [railway.app](https://railway.app)
- [ ] Connect GitHub account
- [ ] Verify email

### Streamlit Cloud (Frontend Hosting)
- [ ] Sign up at [share.streamlit.io](https://share.streamlit.io)
- [ ] Connect GitHub account
- [ ] Verify email

---

## Phase 2: Local Preparation (10 minutes)

### Backend Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Add PostgreSQL connection string
- [ ] Add Cloudinary credentials
- [ ] Add SendGrid API key
- [ ] Add Sentry DSN (optional)
- [ ] Generate SECRET_KEY: `openssl rand -hex 32`

### Test Locally
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Migrate database: `python migrate_to_postgres.py`
- [ ] Test backend: `python main.py`
- [ ] Visit http://localhost:8000/docs
- [ ] Test an API endpoint

### Frontend Prep
- [ ] Update `frontend/config.py` (already done)
- [ ] Test locally: `streamlit run Home.py`
- [ ] Verify database connection
- [ ] Test a feature

---

## Phase 3: Backend Deployment (15 minutes)

### Railway Setup
- [ ] Create new project on Railway
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose `Kilele Project` repository
- [ ] Set root directory to `backend`

### Add PostgreSQL
- [ ] Click "+ New" in Railway
- [ ] Select "Database" → "PostgreSQL"
- [ ] Wait for provisioning

### Configure Environment
Add these variables in Railway:
- [ ] `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
- [ ] `SECRET_KEY` = (from .env)
- [ ] `CLOUDINARY_CLOUD_NAME` = (from Cloudinary)
- [ ] `CLOUDINARY_API_KEY` = (from Cloudinary)
- [ ] `CLOUDINARY_API_SECRET` = (from Cloudinary)
- [ ] `SENDGRID_API_KEY` = (from SendGrid)
- [ ] `FROM_EMAIL` = `noreply@kilele.app`
- [ ] `SENTRY_DSN` = (from Sentry, optional)
- [ ] `SENTRY_ENVIRONMENT` = `production`
- [ ] `ENVIRONMENT` = `production`
- [ ] `DEBUG` = `False`
- [ ] `CORS_ORIGINS` = (will add Streamlit URL later)

### Deploy
- [ ] Click "Deploy" or push to GitHub
- [ ] Wait for build (3-5 minutes)
- [ ] Check logs for errors
- [ ] Copy Railway URL: `https://your-app.railway.app`
- [ ] Test: Visit URL in browser
- [ ] Test: Visit `/docs` endpoint

---

## Phase 4: Frontend Deployment (10 minutes)

### Push to GitHub
- [ ] Commit all changes: `git add .`
- [ ] Commit: `git commit -m "Production ready v2.0"`
- [ ] Push: `git push origin main`

### Streamlit Cloud Deploy
- [ ] Go to [share.streamlit.io](https://share.streamlit.io)
- [ ] Click "New app"
- [ ] Select repository: `Kilele Project`
- [ ] Branch: `main`
- [ ] Main file: `frontend/Home.py`

### Add Secrets
Click "Advanced settings" → "Secrets", paste:
```toml
DATABASE_URL = "your-postgres-connection-string"
CLOUDINARY_CLOUD_NAME = "your-cloud-name"
CLOUDINARY_API_KEY = "your-api-key"
CLOUDINARY_API_SECRET = "your-api-secret"
SENTRY_DSN = "your-sentry-dsn"
ENVIRONMENT = "production"
DEBUG = "False"
API_BASE_URL = "https://your-backend.railway.app"
```

### Deploy
- [ ] Click "Deploy!"
- [ ] Wait for deployment (3-5 minutes)
- [ ] Copy Streamlit URL: `https://your-app.streamlit.app`
- [ ] Test: Open URL in browser
- [ ] Test: Try logging in

---

## Phase 5: Connect Services (5 minutes)

### Update CORS
- [ ] Go back to Railway
- [ ] Add variable: `CORS_ORIGINS` = `https://your-app.streamlit.app`
- [ ] Redeploy backend

### Migrate Data
If you have existing data:
- [ ] Set environment: `$env:DATABASE_URL="production-url"`
- [ ] Run: `python migrate_to_postgres.py`
- [ ] Verify data in production

---

## Phase 6: Testing (10 minutes)

### Core Features
- [ ] Register new account
- [ ] Login/logout
- [ ] View trails
- [ ] Bookmark a trail
- [ ] Add a review
- [ ] Upload profile picture
- [ ] Test on mobile device

### Admin Features
- [ ] Make yourself admin: `python make_admin.py`
- [ ] Access Admin Dashboard
- [ ] Add a new trail
- [ ] Upload trail image to Cloudinary

### Email Testing
- [ ] Request password reset
- [ ] Check email received
- [ ] Test reset link works

### Error Tracking
- [ ] Cause an error intentionally
- [ ] Check Sentry dashboard
- [ ] Verify error captured

---

## Phase 7: Post-Deployment (30 minutes)

### Content
- [ ] Add real Kenyan trail data
- [ ] Upload professional photos
- [ ] Write detailed trail descriptions
- [ ] Add GPS coordinates
- [ ] Set difficulty levels

### Monitoring Setup
- [ ] Bookmark Sentry dashboard
- [ ] Set up Sentry email alerts
- [ ] Bookmark Railway metrics
- [ ] Bookmark Streamlit analytics

### Backups
- [ ] Test backup: `python backup_service.py create`
- [ ] Verify backup created
- [ ] Set up automated backups (Task Scheduler)
- [ ] Test restore: `python backup_service.py restore <file>`

### Documentation
- [ ] Update README with live URL
- [ ] Create user guide
- [ ] Document admin procedures
- [ ] Write changelog

---

## Phase 8: Launch (When Ready)

### Pre-Launch
- [ ] Test thoroughly
- [ ] Fix any bugs
- [ ] Add sample data
- [ ] Prepare announcement

### Launch
- [ ] Share URL with friends
- [ ] Post on social media
- [ ] Gather feedback
- [ ] Monitor errors

### Post-Launch
- [ ] Daily error check (Sentry)
- [ ] Weekly backup verification
- [ ] Monthly usage review
- [ ] Respond to user feedback

---

## 🎉 Success Criteria

You've successfully deployed when:
- ✅ Users can register and login
- ✅ All trails are visible
- ✅ Images load from Cloudinary
- ✅ Emails are sent
- ✅ No critical errors in Sentry
- ✅ Mobile UI works perfectly
- ✅ Database is backed up
- ✅ App is publicly accessible

---

## 📊 Monitoring Checklist

### Daily
- [ ] Check Sentry for new errors
- [ ] Review Railway logs
- [ ] Monitor Cloudinary usage

### Weekly
- [ ] Verify backup creation
- [ ] Review user activity
- [ ] Check email delivery rate
- [ ] Monitor database size

### Monthly
- [ ] Review costs (should be $0-5)
- [ ] Clean old backups
- [ ] Update dependencies
- [ ] Review performance metrics

---

## 🆘 Emergency Contacts

### Services
- **Railway**: https://railway.app/help
- **Streamlit**: https://docs.streamlit.io
- **Neon**: https://neon.tech/docs
- **Cloudinary**: https://support.cloudinary.com
- **SendGrid**: https://support.sendgrid.com
- **Sentry**: https://sentry.io/support

### Documentation
- **Full Guide**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **Quick Start**: [QUICKSTART_V2.md](QUICKSTART_V2.md)
- **Environment**: [.env.example](.env.example)

---

## 📝 Notes

Use this space for your deployment-specific notes:

**API URL**: ___________________________________________

**Frontend URL**: ___________________________________________

**Database URL**: ___________________________________________

**Cloudinary Name**: ___________________________________________

**Admin Username**: ___________________________________________

**Deployment Date**: ___________________________________________

**Last Backup**: ___________________________________________

---

**Status**: [ ] Not Started | [ ] In Progress | [ ] Completed | [ ] Live! 🎉

**Total Time**: ~45 minutes for complete deployment

**Good luck! 🏔️**
