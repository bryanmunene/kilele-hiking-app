# 🚀 DEPLOY NOW - Step by Step Instructions

**Time needed:** 45 minutes  
**Your GitHub Repo:** https://github.com/bryanmunene/kilele-hiking-app

---

## Part 1: Deploy Backend to Railway (20 minutes)

### Step 1: Go to Railway
1. Open https://railway.app in your browser
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub

### Step 2: Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **"bryanmunene/kilele-hiking-app"**
4. Railway will detect it's a Python project

### Step 3: Configure Root Directory
1. Click on the deployed service
2. Go to **"Settings"** tab
3. Find **"Root Directory"**
4. Set it to: `backend`
5. Click **"Save"**

### Step 4: Add Environment Variables
1. Click **"Variables"** tab
2. Click **"Add Variable"** for each of these:

```
DATABASE_URL = sqlite:///./kilele.db
API_HOST = 0.0.0.0
PORT = ${{PORT}}
DEBUG = False
SECRET_KEY = kilele_hiking_app_secret_key_production_2026
STRAVA_CLIENT_ID = 199882
STRAVA_CLIENT_SECRET = 5ddc762ef5621ee2ad9de18e19b3adb4c05691e9
STRAVA_REDIRECT_URI = https://kilele-app.streamlit.app/strava/callback
STRAVA_WEBHOOK_VERIFY_TOKEN = kilele_strava_webhook_2026
```

3. Click **"Save"** after each one

### Step 5: Deploy
1. Railway will automatically deploy
2. Wait 3-5 minutes for deployment to complete
3. Click on **"Settings"** → **"Networking"**
4. Click **"Generate Domain"**
5. **COPY THIS URL** - You'll need it! (e.g., `kilele-backend-production.up.railway.app`)

---

## Part 2: Deploy Frontend to Streamlit Cloud (15 minutes)

### Step 1: Go to Streamlit Cloud
1. Open https://share.streamlit.io in your browser
2. Click **"Sign in"** → **"Continue with GitHub"**
3. Authorize Streamlit Cloud

### Step 2: Create New App
1. Click **"New app"**
2. Repository: Select **"bryanmunene/kilele-hiking-app"**
3. Branch: **"main"**
4. Main file path: **"frontend/Home.py"**
5. App URL: Choose a name like **"kilele-app"** or **"kilele-hiking"**

### Step 3: Advanced Settings (Optional but Recommended)
1. Click **"Advanced settings..."**
2. Python version: **3.12**
3. Click **"Save"**

### Step 4: Deploy
1. Click **"Deploy!"**
2. Wait 5-10 minutes for first deployment
3. **COPY YOUR APP URL** when it appears (e.g., `https://kilele-app.streamlit.app`)

---

## Part 3: Update Configuration (10 minutes)

You need to update one file to connect frontend to backend.

### Create API Configuration File

I'll do this for you in the next step, but you'll need your Railway backend URL from Part 1, Step 5.

**Your Railway Backend URL:** _________________________

---

## Part 4: Test Your Deployment (10 minutes)

### Step 1: Open Your App
1. Go to your Streamlit Cloud URL
2. You should see the Kilele homepage
3. Click around to make sure it loads

### Step 2: Test Registration
1. Click **"🔐 Login"** in sidebar
2. Click **"Create new account"**
3. Register with test credentials
4. Verify you can login

### Step 3: Test Trail Browsing
1. Browse trails in the app
2. Click on a trail to see details
3. Verify images and information load

### Step 4: Test Offline Preparation
1. Go to **"📍 Track Hike"**
2. Select a trail
3. Click **"📥 Download"** button
4. Verify you see "✅ Ready for offline use"

---

## ✅ SUCCESS CHECKLIST:

- [ ] Backend deployed to Railway
- [ ] Railway domain generated
- [ ] Frontend deployed to Streamlit Cloud
- [ ] Streamlit app URL accessible
- [ ] Can register new user
- [ ] Can browse trails
- [ ] Can download trail for offline
- [ ] No error messages

---

## 🎉 NEXT STEPS:

Once deployed:

1. **Share the URL** with your test users
2. **Test on mobile phones** (Android & iOS)
3. **Test offline mode** (turn off WiFi after downloading)
4. **Monitor for bugs** throughout the week
5. **Be ready for Saturday!**

---

## ⚠️ IF SOMETHING GOES WRONG:

### Backend Won't Deploy:
- Check Railway logs (click on service → "Logs" tab)
- Make sure all environment variables are set
- Verify root directory is "backend"

### Frontend Won't Deploy:
- Check Streamlit Cloud logs (visible during deployment)
- Make sure main file path is "frontend/Home.py"
- Verify Python version is 3.12

### Can't Connect Backend to Frontend:
- Make sure you updated the Strava redirect URI
- Check that Railway domain is accessible
- We'll fix API URL in next step

---

## 📞 NEED HELP?

I'm here! Just let me know:
- What step you're on
- Any error messages you see
- Screenshots if helpful

**Let's get this deployed! Start with Part 1 (Railway) and let me know when you have your backend URL.** 🚀
