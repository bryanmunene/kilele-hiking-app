# Strava Integration Setup Guide

## Current Status
❌ **Strava integration is not configured** - The error "Failed to get authorization URL" occurs because Strava API credentials are missing.

## Quick Fix Steps

### 1. Get Strava API Credentials

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Log in with your Strava account
3. Click **"Create An App"** or edit your existing app
4. Fill in the application details:
   - **Application Name**: Kilele Hiking App
   - **Category**: Training
   - **Club**: Leave blank
   - **Website**: http://localhost:8501 (or your domain)
   - **Authorization Callback Domain**: `localhost` (or your domain without http://)
5. Click **Create** or **Update**
6. You'll see your **Client ID** and **Client Secret**

### 2. Add Credentials to Backend

Edit `backend/.env` file and uncomment/add these lines:

```bash
# Strava API Integration
STRAVA_CLIENT_ID=12345  # Replace with your actual Client ID
STRAVA_CLIENT_SECRET=abcdef123456789  # Replace with your actual Client Secret
STRAVA_REDIRECT_URI=http://localhost:8501/strava/callback
STRAVA_WEBHOOK_VERIFY_TOKEN=kilele_strava_webhook_2026  # Any random string
```

### 3. Restart Backend Server

```powershell
# Stop the backend if running (Ctrl+C)
# Then restart:
cd backend
python main.py
```

The backend will now show:
```
INFO: Strava integration enabled
```

### 4. Test Connection

1. Go to the Streamlit app: http://localhost:8501
2. Navigate to **Strava** page (🟠 in sidebar)
3. Click **"Connect Strava"** button
4. You should now see the authorization link instead of an error
5. Click the authorization link to connect

## Without Strava Setup (Optional Feature)

If you don't want to use Strava integration, that's fine! The app will continue to work normally. The Strava page will show:

> ⚙️ **Configuration Required**
> 
> Strava integration is not yet configured.

All other features (trail browsing, bookmarks, social features, etc.) will work perfectly without Strava.

## Troubleshooting

### Error: "Failed to get authorization URL"
**Cause**: Strava credentials not configured in backend `.env`
**Fix**: Follow steps 1-3 above

### Error: "Cannot connect to backend server"
**Cause**: Backend is not running
**Fix**: Start backend with `cd backend && python main.py`

### Error: "Invalid client_id"
**Cause**: Wrong Client ID in `.env` file
**Fix**: Double-check the Client ID from Strava API settings

### Error: "Bad Request - redirect_uri mismatch"
**Cause**: Redirect URI doesn't match what's set in Strava app settings
**Fix**: Make sure the callback domain in Strava settings matches your `STRAVA_REDIRECT_URI`

## Production Deployment

For production, update these values:

```bash
STRAVA_REDIRECT_URI=https://yourdomain.com/strava/callback
```

And in Strava API settings, update:
- **Website**: https://yourdomain.com
- **Authorization Callback Domain**: yourdomain.com

## Features Enabled by Strava

Once configured, users can:
- ✅ Auto-sync hiking activities from Strava
- ✅ Import GPS routes, stats, and photos
- ✅ Match Strava activities to Kilele trails automatically
- ✅ Track combined achievements across platforms
- ✅ Real-time activity updates via webhooks
- ✅ View all activities in one dashboard

---

**Note**: Strava integration is completely optional. The Kilele app works perfectly fine without it for users who don't use Strava.
