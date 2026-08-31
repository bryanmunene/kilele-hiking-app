# 🚀 QUICK DEPLOYMENT GUIDE

## ✅ Your App is Ready for Deployment!

All necessary files have been created. Follow these steps to deploy:

---

## 📋 Pre-Deployment Setup

### 1. Your Generated Secret Key (SAVE THIS!)
```
SECRET_KEY=<GENERATE_A_STRONG_RANDOM_VALUE>
```

### 2. Initialize Git Repository
```bash
cd "c:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project"
git init
git add .
git commit -m "Initial commit - Kilele Hiking App"
```

### 3. Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., "kilele-hiking-app")
3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/kilele-hiking-app.git
git branch -M main
git push -u origin main
```

---

## 🚂 Deploy Backend (Railway - Recommended)

### Option A: Using Railway Dashboard (Easiest)

1. **Sign Up**: Go to https://railway.app and sign up with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your kilele-hiking-app repository
   - Select the `backend` folder as root

3. **Add PostgreSQL**:
   - In your project dashboard
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically sets `DATABASE_URL`

4. **Configure Environment Variables**:
   Go to your service → Variables → Add:
   ```
   SECRET_KEY=<GENERATE_A_STRONG_RANDOM_VALUE>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ALLOWED_ORIGINS=*
   ```
   (Update ALLOWED_ORIGINS after deploying frontend)

5. **Deploy**:
   - Railway auto-deploys on push
   - Wait for build to complete
   - Get your backend URL (e.g., `https://kilele-backend.up.railway.app`)

6. **Seed Database**:
   - Go to project → service → Terminal
   - Run: `python seed_data.py`

### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Add PostgreSQL
railway add

# Set environment variables
railway variables set SECRET_KEY=<GENERATE_A_STRONG_RANDOM_VALUE>

# Deploy
railway up
```

**Backend URL**: Save this for frontend configuration!

---

## 🎨 Deploy Frontend (Streamlit Cloud - Free)

1. **Update Secrets File**:
   Edit `frontend/.streamlit/secrets.toml`:
   ```toml
   API_BASE_URL = "https://YOUR-BACKEND-URL.railway.app/api/v1"
   ```
   Replace with your actual Railway backend URL

2. **Push Changes**:
   ```bash
   git add .
   git commit -m "Update API URL for production"
   git push
   ```

3. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your GitHub repository
   - Set:
     - Main file path: `frontend/Home.py`
     - Python version: 3.12
   
4. **Configure Secrets** (in Streamlit Cloud dashboard):
   - Go to App settings → Secrets
   - Add:
   ```toml
   API_BASE_URL = "https://YOUR-BACKEND-URL.railway.app/api/v1"
   ```

5. **Deploy**:
   - Click "Deploy"
   - Wait for deployment (2-3 minutes)
   - Your app will be live at: `https://YOUR-APP.streamlit.app`

---

## 🔄 Update CORS on Backend

Once frontend is deployed:

1. Go to Railway dashboard
2. Update `ALLOWED_ORIGINS` variable:
   ```
   ALLOWED_ORIGINS=https://YOUR-APP.streamlit.app
   ```
3. Save and redeploy

---

## ✅ Post-Deployment Checklist

Test these features on your live app:

- [ ] Homepage loads correctly
- [ ] User registration works
- [ ] Login and 2FA setup
- [ ] Browse trails
- [ ] View trail details on map
- [ ] Add new trail (admin)
- [ ] Upload profile picture
- [ ] Post reviews
- [ ] Send messages
- [ ] Import wearable device file
- [ ] View analytics dashboard

---

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check `API_BASE_URL` in Streamlit secrets
- Verify backend is deployed and running
- Check Railway logs for errors

### Database errors
- Ensure PostgreSQL is added in Railway
- Run `python seed_data.py` in Railway terminal
- Check DATABASE_URL is set correctly

### CORS errors
- Update ALLOWED_ORIGINS with frontend URL
- Don't forget the `https://` prefix
- Restart backend after updating

---

## 📊 Monitor Your Deployment

### Railway (Backend)
- View logs: Dashboard → Your service → Logs
- Check metrics: Dashboard → Metrics
- Restart: Dashboard → Settings → Restart

### Streamlit Cloud (Frontend)
- View logs: App menu (☰) → Manage app → Logs
- Restart: App menu → Reboot app
- Update: Push to GitHub (auto-deploys)

---

## 💰 Costs

**Current Setup (Free Tier):**
- Railway: $5 credit/month (free trial)
- Streamlit Cloud: Free for public apps
- **Total: $0-5/month**

**Upgrade When Needed:**
- Railway Pro: $20/month
- Streamlit Cloud Teams: $200/month

---

## 🎉 You're Done!

Your app should now be live at:
- **Frontend**: https://YOUR-APP.streamlit.app
- **Backend**: https://YOUR-BACKEND.railway.app
- **API Docs**: https://YOUR-BACKEND.railway.app/docs

Share with friends and start hiking! 🏔️

---

## 📚 Additional Resources

- Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Railway docs: https://docs.railway.app
- Streamlit docs: https://docs.streamlit.io
- FastAPI docs: https://fastapi.tiangolo.com

---

**Questions or issues?** 
Check the detailed [DEPLOYMENT.md](DEPLOYMENT.md) guide for more options and troubleshooting.
