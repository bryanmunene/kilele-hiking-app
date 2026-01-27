# 🚀 Deploy Kilele App - Streamlit Cloud Method

## ✨ What You'll Get
- **Frontend**: Free hosting on Streamlit Cloud
- **Backend**: Free tier on Railway (includes PostgreSQL)
- **Total Setup Time**: 15 minutes
- **Cost**: FREE for first month, then ~$5/month

---

## 📋 Prerequisites

1. **GitHub Account** (create at https://github.com)
2. **Railway Account** (create at https://railway.app - login with GitHub)
3. **Streamlit Cloud Account** (create at https://share.streamlit.io - login with GitHub)

That's it! Everything is done through web interfaces - no command line needed!

---

## 🎬 Step 1: Push to GitHub (One-Time Setup)

### Option A: Using GitHub Desktop (Easiest)

1. **Download GitHub Desktop**: https://desktop.github.com
2. **Install and login** with your GitHub account
3. **Add your project**:
   - File → Add Local Repository
   - Browse to: `C:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project`
   - Click "Add Repository"
4. **Publish**:
   - Click "Publish repository"
   - Name: `kilele-hiking-app`
   - Uncheck "Keep this code private" (for free Streamlit)
   - Click "Publish repository"

Done! Your code is now on GitHub.

### Option B: Using Git Command Line

Open PowerShell and run:

```powershell
cd "C:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Kilele Hiking App"

# Create GitHub repo (go to github.com/new first)
git remote add origin https://github.com/YOUR_USERNAME/kilele-hiking-app.git
git branch -M main
git push -u origin main
```

---

## 🚂 Step 2: Deploy Backend (Railway)

### 2.1 Create Railway Project

1. **Go to**: https://railway.app
2. **Click**: "Login" → Login with GitHub
3. **Click**: "New Project"
4. **Select**: "Deploy from GitHub repo"
5. **Choose**: Your `kilele-hiking-app` repository
6. **Click**: "Deploy Now"

### 2.2 Configure Root Directory

Railway will try to deploy the whole project. We need to tell it to use only the `backend` folder:

1. Click on your deployed service
2. Go to **Settings** tab
3. Find **"Root Directory"**
4. Enter: `backend`
5. Click **"Update"**
6. Railway will automatically redeploy

### 2.3 Add PostgreSQL Database

1. In your Railway project dashboard
2. Click **"New"** button
3. Select **"Database"**
4. Choose **"Add PostgreSQL"**
5. Railway automatically connects it to your backend (sets `DATABASE_URL`)

### 2.4 Add Environment Variables

1. Click on your backend service
2. Go to **"Variables"** tab
3. Click **"New Variable"** and add these:

```
SECRET_KEY=fe8abec15c9f12e6ef3e47924342c2e90f2cfcae9f90d22171438a69ff0e3f90
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=*
```

4. Click **"Add"** for each variable

### 2.5 Get Your Backend URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. **Copy the URL** (e.g., `kilele-backend.up.railway.app`)

**Save this URL! You'll need it for frontend.**

### 2.6 Seed the Database

1. Click on your backend service
2. Go to **"Deployments"** tab
3. Wait for "SUCCESS" status
4. Click on the latest deployment
5. Open the **"View Logs"** tab
6. Click **"Terminal"** (or go to Settings → Terminal)
7. Run: `python seed_data.py`

Your backend is now live! 🎉

---

## 🎨 Step 3: Deploy Frontend (Streamlit Cloud)

### 3.1 Update API URL in Code

Before deploying, we need to tell your frontend where the backend is:

1. **Open**: `frontend/.streamlit/secrets.toml`
2. **Replace** the URL with your Railway backend URL:
   ```toml
   API_BASE_URL = "https://kilele-backend.up.railway.app/api/v1"
   ```
   (Use YOUR actual Railway URL from Step 2.5)

3. **Save the file**

4. **Push to GitHub**:
   - If using GitHub Desktop: Commit and Push
   - If using command line:
     ```powershell
     git add .
     git commit -m "Update API URL for production"
     git push
     ```

### 3.2 Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Click**: "Sign in" → Login with GitHub
3. **Click**: "New app" (top right)
4. **Fill in**:
   - **Repository**: `YOUR_USERNAME/kilele-hiking-app`
   - **Branch**: `main`
   - **Main file path**: `frontend/Home.py`
   - **App URL** (optional): Choose a custom name like `kilele-app`

5. **Click**: "Deploy!"

### 3.3 Add Secrets to Streamlit

While the app is deploying:

1. Click on **"⋮"** (three dots) next to your app
2. Select **"Settings"**
3. Go to **"Secrets"** section
4. Paste this (with YOUR Railway URL):
   ```toml
   API_BASE_URL = "https://kilele-backend.up.railway.app/api/v1"
   ```
5. Click **"Save"**

### 3.4 Wait for Deployment

- Deployment takes 2-3 minutes
- You'll see a progress bar
- When done, your app URL will be: `https://kilele-app.streamlit.app`

Your frontend is now live! 🎉

---

## 🔄 Step 4: Final Configuration

### Update CORS on Backend

Now that your frontend is live, update the backend to accept requests from it:

1. **Go to Railway** → Your backend service
2. **Variables** tab
3. **Find**: `ALLOWED_ORIGINS`
4. **Update to**: `https://YOUR-APP.streamlit.app`
   (Replace with your actual Streamlit URL)
5. Backend will automatically redeploy

---

## ✅ Step 5: Test Your Live App!

Visit your Streamlit URL and test:

1. ✅ Homepage loads
2. ✅ Register a new account
3. ✅ Login
4. ✅ Browse trails
5. ✅ Upload profile picture
6. ✅ Add a review
7. ✅ Send a message
8. ✅ Import a wearable file

---

## 🎯 Your Live URLs

Once deployed, you'll have:

- **App**: `https://YOUR-APP.streamlit.app`
- **API**: `https://YOUR-BACKEND.up.railway.app`
- **API Docs**: `https://YOUR-BACKEND.up.railway.app/docs`

---

## 🔄 How to Update Your App

### Update Frontend (Streamlit)

1. Make changes locally
2. Push to GitHub (Desktop or command line)
3. Streamlit auto-deploys in ~2 minutes!

### Update Backend (Railway)

1. Make changes locally
2. Push to GitHub
3. Railway auto-deploys in ~3 minutes!

---

## 💰 Costs Breakdown

| Service | Free Tier | Paid Plan |
|---------|-----------|-----------|
| **Streamlit Cloud** | ✅ Unlimited (public apps) | $200/month (private) |
| **Railway** | $5 credit/month | $20/month |
| **PostgreSQL** | ✅ Included with Railway | Included |
| **Total** | ~$0-5/month | $220/month |

**Recommendation**: Start with free/cheap tier, upgrade when you have users!

---

## 🐛 Troubleshooting

### Frontend Shows "Connection Error"

**Solution**:
1. Check backend is running (visit Railway URL)
2. Verify API_BASE_URL in Streamlit secrets
3. Check Railway logs for errors

### "Database Connection Error" on Backend

**Solution**:
1. Ensure PostgreSQL is added in Railway
2. Check if `DATABASE_URL` variable exists
3. Run `python seed_data.py` in Railway terminal

### CORS Error in Browser Console

**Solution**:
1. Update `ALLOWED_ORIGINS` in Railway variables
2. Use your exact Streamlit URL (with https://)
3. Wait 1-2 minutes for Railway to redeploy

### Need to Reseed Database

**Railway Terminal**:
1. Go to backend service → Settings → Terminal
2. Run: `python seed_data.py`

---

## 📊 Monitoring Your App

### View Logs

**Streamlit**:
- App menu (☰) → Manage app → Logs

**Railway**:
- Service → Deployments → Latest → View Logs

### Restart Services

**Streamlit**:
- App menu (☰) → Reboot app

**Railway**:
- Service → Settings → Restart

---

## 🆘 Need Help?

- **Railway Docs**: https://docs.railway.app
- **Streamlit Docs**: https://docs.streamlit.io
- **GitHub Issues**: Create an issue in your repo

---

## 🎉 You're Live!

Share your app:
- `https://YOUR-APP.streamlit.app`

Tweet it, share with friends, and start hiking! 🏔️

---

## 🚀 Next Steps (Optional)

1. **Custom Domain**: 
   - Streamlit: Settings → Custom domain
   - Railway: Settings → Domains → Custom domain

2. **Analytics**:
   - Add Google Analytics to Streamlit app
   - Monitor usage in Streamlit Cloud dashboard

3. **Backups**:
   - Railway auto-backs up PostgreSQL
   - Export data periodically via API

4. **Upgrades**:
   - When you hit limits, upgrade plans
   - Railway: More compute/memory
   - Streamlit: Private apps, more resources

---

**Congratulations!** 🎊 Your hiking app is now live on the internet!
