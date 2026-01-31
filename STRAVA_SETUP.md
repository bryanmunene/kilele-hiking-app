# 🟠 Strava Integration Setup Guide

Complete guide to setting up Strava integration for the Kilele Hiking App.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step 1: Create Strava API Application](#step-1-create-strava-api-application)
- [Step 2: Configure Backend](#step-2-configure-backend)
- [Step 3: Configure Frontend](#step-3-configure-frontend)
- [Step 4: Set Up Webhooks (Optional)](#step-4-set-up-webhooks-optional)
- [Step 5: Test Integration](#step-5-test-integration)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Strava integration allows users to:
- **Connect their Strava account** via OAuth 2.0
- **Auto-sync hiking activities** from Strava to Kilele
- **Match activities to trails** using GPS proximity
- **Import activity data** (distance, time, elevation, photos, kudos)
- **Receive real-time updates** via webhooks
- **Track combined statistics** across both platforms

### Architecture
- **Backend**: FastAPI with `stravalib` library
- **Database**: 3 new models (`StravaToken`, `StravaActivity`, `StravaWebhookSubscription`)
- **Frontend**: Streamlit page (`19_🟠_Strava.py`) with OAuth flow
- **Scheduler**: Background job runs hourly to auto-sync enabled users

---

## Prerequisites

1. **Strava Account**: Create a free account at [strava.com](https://www.strava.com)
2. **Backend Running**: FastAPI server must be operational
3. **Database Migrated**: New Strava models added to database
4. **Python Packages**:
   ```bash
   # Backend
   stravalib==1.6.0
   requests==2.32.3
   apscheduler==3.10.4
   
   # Frontend
   stravalib==1.6.0
   ```

---

## Step 1: Create Strava API Application

### 1.1 Navigate to API Settings
Go to: [strava.com/settings/api](https://www.strava.com/settings/api)

### 1.2 Fill Out Application Details

| Field | Value | Notes |
|-------|-------|-------|
| **Application Name** | Kilele Hiking App | Choose any name |
| **Category** | Social Network | Select from dropdown |
| **Club** | Leave empty | Optional |
| **Website** | https://your-domain.com | Your app's URL |
| **Authorization Callback Domain** | `localhost` (dev)<br>`your-domain.com` (prod) | **Critical**: Must match redirect URI domain |

### 1.3 Accept Terms
- Read and accept the **API Agreement**
- Click **Create**

### 1.4 Save Credentials
After creation, you'll see:
- **Client ID**: `12345` (example)
- **Client Secret**: `abc123xyz...` (keep secret!)
- **Access Token**: (not needed - OAuth generates per-user tokens)

**⚠️ IMPORTANT**: Never commit `Client Secret` to GitHub!

---

## Step 2: Configure Backend

### 2.1 Update Environment Variables

Create/edit `backend/.env`:

```bash
# Strava API Credentials
STRAVA_CLIENT_ID=12345
STRAVA_CLIENT_SECRET=your_secret_here_do_not_share

# Redirect URI (must match Authorization Callback Domain)
# Development
STRAVA_REDIRECT_URI=http://localhost:8501/strava/callback

# Production
# STRAVA_REDIRECT_URI=https://your-app.streamlit.app/strava/callback

# Webhook Verification Token (generate random string)
STRAVA_WEBHOOK_VERIFY_TOKEN=my_secure_random_token_123
```

### 2.2 Generate Webhook Verify Token

```bash
# Generate secure random token
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: 8xK9mN3pQ5rT2wV7yZ1aB4cD6eF0gH
```

### 2.3 Verify Configuration File

Check `backend/config.py` includes:

```python
# Strava API Configuration
STRAVA_CLIENT_ID: str = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET: str = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI: str = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8501/strava/callback")
STRAVA_WEBHOOK_VERIFY_TOKEN: str = os.getenv("STRAVA_WEBHOOK_VERIFY_TOKEN", "")
```

### 2.4 Restart Backend

```powershell
cd backend
..\\.venv\Scripts\Activate.ps1
python main.py
```

Look for startup log:
```
🟠 Strava auto-sync scheduler started
```

---

## Step 3: Configure Frontend

### 3.1 Update API Base URL

Edit `frontend/pages/19_🟠_Strava.py`:

```python
# Development
API_BASE_URL = "http://localhost:8000"

# Production (update after deploying backend)
# API_BASE_URL = "https://your-backend.herokuapp.com"
```

### 3.2 Test Frontend

```powershell
cd frontend
..\.venv\Scripts\Activate.ps1
streamlit run Home.py
```

Navigate to **🟠 Strava** page in sidebar.

---

## Step 4: Set Up Webhooks (Optional)

Webhooks enable **real-time activity updates** when users complete activities on Strava.

### 4.1 Prerequisites
- Backend deployed to public URL (e.g., Heroku, Railway, Render)
- HTTPS enabled (required by Strava)

### 4.2 Subscribe to Webhook

```bash
curl -X POST https://www.strava.com/api/v3/push_subscriptions \
  -F client_id=YOUR_CLIENT_ID \
  -F client_secret=YOUR_CLIENT_SECRET \
  -F callback_url=https://your-backend.com/api/strava/webhook \
  -F verify_token=YOUR_WEBHOOK_VERIFY_TOKEN
```

**Response**:
```json
{
  "id": 67890,
  "resource_state": 2,
  "application_id": 12345,
  "callback_url": "https://your-backend.com/api/strava/webhook",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

### 4.3 Save Subscription ID

Add to `backend/.env`:
```bash
STRAVA_WEBHOOK_SUBSCRIPTION_ID=67890
```

### 4.4 Verify Webhook

Strava will send GET request to verify:
```
GET /api/strava/webhook?hub.mode=subscribe&hub.challenge=abc123&hub.verify_token=YOUR_TOKEN
```

Backend responds with:
```json
{"hub.challenge": "abc123"}
```

### 4.5 View Subscriptions

```bash
curl -G https://www.strava.com/api/v3/push_subscriptions \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET
```

### 4.6 Delete Subscription (if needed)

```bash
curl -X DELETE https://www.strava.com/api/v3/push_subscriptions/SUBSCRIPTION_ID \
  -F client_id=YOUR_CLIENT_ID \
  -F client_secret=YOUR_CLIENT_SECRET
```

---

## Step 5: Test Integration

### 5.1 Connect Strava Account

1. **Login** to Kilele app (frontend)
2. Navigate to **🟠 Strava** page
3. Click **Connect Strava** button
4. Authorize on Strava:
   - Grants `activity:read_all` permission
   - Redirects back to Kilele
5. Refresh page - should show "✅ Connected"

### 5.2 Sync Activities

1. Click **🔄 Sync Now** button
2. Select days (7-365)
3. Wait for sync to complete
4. View activities in table below

### 5.3 Check Trail Matching

Activities within **5km of trail coordinates** are auto-matched:
- ✅ Green checkmark = Matched to trail
- ❌ Red X = No nearby trail found

### 5.4 Verify Auto-Sync

1. Enable **auto-sync** toggle
2. Click **Save Settings**
3. Wait 1 hour (scheduler runs hourly)
4. Check logs: `Auto-sync completed`

### 5.5 Test Webhook (if enabled)

1. Complete a hike on Strava mobile app
2. Activity should appear in Kilele within 1 minute
3. Check backend logs:
   ```
   Webhook event received: create activity 123456
   Synced 1 activities
   ```

---

## Troubleshooting

### Issue: "Authorization failed"

**Symptoms**: OAuth redirect shows error

**Causes**:
- Wrong `STRAVA_REDIRECT_URI` in `.env`
- Mismatch between redirect URI and Strava app settings
- Incorrect client ID/secret

**Fix**:
1. Verify `.env` values match Strava app
2. Check redirect URI domain matches **Authorization Callback Domain**
3. Restart backend after `.env` changes

---

### Issue: "No activities synced"

**Symptoms**: Sync completes but 0 activities imported

**Causes**:
- User has no activities in selected date range
- All activities are private
- Activities are not hiking type (Hike, Walk, Trail Run, Run)

**Fix**:
1. Check Strava app for activities
2. Ensure activities are public
3. Increase sync days (e.g., 90 days)
4. Check activity types are supported

---

### Issue: "Webhook not receiving events"

**Symptoms**: Manual sync works, but real-time updates don't

**Causes**:
- Backend not accessible via HTTPS
- Wrong verify token
- Subscription not created
- Firewall blocking requests

**Fix**:
1. Verify backend URL is public and HTTPS
2. Check webhook subscription exists:
   ```bash
   curl -G https://www.strava.com/api/v3/push_subscriptions \
     -d client_id=YOUR_CLIENT_ID \
     -d client_secret=YOUR_CLIENT_SECRET
   ```
3. Test endpoint manually:
   ```bash
   curl https://your-backend.com/api/strava/webhook
   # Should return 200 OK
   ```
4. Check backend logs for incoming requests

---

### Issue: "Rate limit exceeded"

**Symptoms**: Error 429 from Strava API

**Causes**:
- Strava API limits:
  - **200 requests per 15 minutes**
  - **2,000 requests per day**

**Fix**:
1. Reduce sync frequency (default: hourly)
2. Sync fewer days per request
3. Wait 15 minutes before retrying
4. Check `strava_service.py` uses caching

---

### Issue: "Token expired"

**Symptoms**: "Unauthorized" errors after initial connection

**Causes**:
- Access token expired (2-hour lifespan)
- Refresh token not working

**Fix**:
- Automatic: `StravaService.refresh_access_token()` handles this
- Manual: Disconnect and reconnect Strava account
- Check `expires_at` field in `StravaToken` table

---

### Issue: "Trail matching not working"

**Symptoms**: All activities show "❌ Not matched"

**Causes**:
- No trails in database near activity location
- GPS coordinates too far from trails (> 5km)
- Activity missing GPS data (gym activities, manual entries)

**Fix**:
1. Check trail coordinates in database:
   ```sql
   SELECT id, name, latitude, longitude FROM hikes;
   ```
2. Increase matching radius in `strava_service.py`:
   ```python
   # Line ~200
   trail = db.query(Hike).filter(
       Hike.latitude.between(lat - 0.1, lat + 0.1),  # ~10km radius
       Hike.longitude.between(lng - 0.1, lng + 0.1)
   ).first()
   ```
3. Verify activity has GPS polyline:
   ```python
   print(activity.map.polyline)  # Should not be None
   ```

---

## API Rate Limits

Strava enforces strict rate limits:

| Limit Type | Value |
|------------|-------|
| **Short-term** | 200 requests / 15 minutes |
| **Daily** | 2,000 requests / day |
| **Per user** | ~1000 requests / day |

### Best Practices:
- ✅ Sync activities in batches (max 200 per request)
- ✅ Use webhooks to avoid polling
- ✅ Cache activity data locally
- ✅ Implement exponential backoff on errors
- ❌ Don't sync all users simultaneously
- ❌ Don't sync more than 30 days per request

---

## Security Checklist

- [ ] Never commit `.env` file to Git
- [ ] Add `.env` to `.gitignore`
- [ ] Use environment variables for secrets
- [ ] Rotate `STRAVA_WEBHOOK_VERIFY_TOKEN` periodically
- [ ] Validate webhook signatures (optional enhancement)
- [ ] Use HTTPS for production webhooks
- [ ] Store tokens encrypted in database (optional enhancement)
- [ ] Implement token refresh before expiry
- [ ] Log all API errors for monitoring
- [ ] Set up rate limit alerts

---

## Production Deployment

### Backend (Heroku Example)

```bash
# 1. Create Heroku app
heroku create kilele-backend

# 2. Set environment variables
heroku config:set STRAVA_CLIENT_ID=12345
heroku config:set STRAVA_CLIENT_SECRET=your_secret
heroku config:set STRAVA_REDIRECT_URI=https://kilele.streamlit.app/strava/callback
heroku config:set STRAVA_WEBHOOK_VERIFY_TOKEN=your_token

# 3. Deploy
git push heroku main

# 4. Subscribe to webhook
curl -X POST https://www.strava.com/api/v3/push_subscriptions \
  -F client_id=12345 \
  -F client_secret=your_secret \
  -F callback_url=https://kilele-backend.herokuapp.com/api/strava/webhook \
  -F verify_token=your_token
```

### Frontend (Streamlit Cloud)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repo
3. Set main file: `frontend/Home.py`
4. No secrets needed (uses backend API)
5. Update `API_BASE_URL` in `19_🟠_Strava.py`:
   ```python
   API_BASE_URL = "https://kilele-backend.herokuapp.com"
   ```

---

## Monitoring & Logs

### Backend Logs

```bash
# View auto-sync logs
tail -f backend.log | grep "Strava"

# Expected output:
# 2025-01-15 10:00:00 - Strava auto-sync scheduler started
# 2025-01-15 11:00:00 - Starting auto-sync for 5 users
# 2025-01-15 11:01:23 - User 1: Synced 3 activities, matched 2 to trails
```

### Database Queries

```sql
-- Check connected users
SELECT u.username, st.athlete_id, st.sync_enabled, st.last_synced
FROM users u
JOIN strava_tokens st ON st.user_id = u.id;

-- Count synced activities
SELECT COUNT(*) FROM strava_activities;

-- View recent activities
SELECT sa.name, sa.distance_km, sa.activity_type, h.name as trail
FROM strava_activities sa
LEFT JOIN hikes h ON sa.matched_hike_id = h.id
ORDER BY sa.start_date DESC
LIMIT 10;

-- Check webhook subscription
SELECT * FROM strava_webhook_subscriptions;
```

---

## Support & Resources

- **Strava API Docs**: [developers.strava.com](https://developers.strava.com/)
- **stravalib Docs**: [github.com/stravalib/stravalib](https://github.com/stravalib/stravalib)
- **OAuth 2.0 Guide**: [oauth.net/2](https://oauth.net/2/)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)

---

## Quick Reference

### Environment Variables
```bash
STRAVA_CLIENT_ID=12345
STRAVA_CLIENT_SECRET=abc123
STRAVA_REDIRECT_URI=http://localhost:8501/strava/callback
STRAVA_WEBHOOK_VERIFY_TOKEN=random_token_123
```

### API Endpoints
```
GET  /api/strava/connect         - Get OAuth URL
POST /api/strava/callback        - Handle OAuth callback
POST /api/strava/sync            - Sync activities
GET  /api/strava/activities      - List activities
GET  /api/strava/stats           - Get user stats
DELETE /api/strava/disconnect    - Disconnect account
GET  /api/strava/webhook         - Verify webhook
POST /api/strava/webhook         - Receive events
POST /api/strava/toggle-autosync - Enable/disable auto-sync
```

### Scheduler
- **Frequency**: Every hour
- **Sync window**: Last 7 days
- **Eligible users**: `sync_enabled=True`
- **Startup**: Runs 1 minute after app start

---

**Last Updated**: January 2025  
**Version**: 1.0
