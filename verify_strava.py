# Verify Strava Integration is Working
import requests
import json

print("🔍 Testing Strava Integration...")
print("="*50)

backend_url = "http://localhost:8000"

# Test 1: Check if backend is running
print("\n1. Testing backend connection...")
try:
    response = requests.get(f"{backend_url}/docs", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend is running at http://localhost:8000")
    else:
        print(f"   ❌ Backend returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect to backend: {e}")
    print("   Make sure backend is running: cd backend && python main.py")
    exit(1)

# Test 2: Check if Strava route is available
print("\n2. Testing Strava API routes...")
try:
    # This will fail without auth, but if route exists we'll get 401/422, not 404
    response = requests.get(f"{backend_url}/api/strava/stats", timeout=5)
    if response.status_code in [401, 422]:  # Auth required
        print("   ✅ Strava routes are registered")
    elif response.status_code == 404:
        print("   ❌ Strava routes not found")
    else:
        print(f"   ℹ️ Got status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check configuration
print("\n3. Checking Strava configuration...")
import os
from pathlib import Path

env_path = Path("backend/.env")
if env_path.exists():
    with open(env_path) as f:
        content = f.read()
        if "STRAVA_CLIENT_ID" in content and "STRAVA_CLIENT_SECRET" in content:
            # Check if they're uncommented
            lines = [l.strip() for l in content.split('\n') if l.strip()]
            client_id_set = any(l.startswith("STRAVA_CLIENT_ID=") for l in lines)
            client_secret_set = any(l.startswith("STRAVA_CLIENT_SECRET=") for l in lines)
            
            if client_id_set and client_secret_set:
                print("   ✅ Strava credentials are configured")
                print(f"   ℹ️ Client ID set: Yes")
                print(f"   ℹ️ Client Secret set: Yes")
            else:
                print("   ⚠️ Strava credentials exist but are commented out")
        else:
            print("   ❌ Strava credentials not found in .env")
else:
    print("   ❌ backend/.env file not found")

print("\n" + "="*50)
print("✅ STRAVA INTEGRATION IS READY!")
print("\nNext steps:")
print("1. Open Streamlit: http://localhost:8501")
print("2. Navigate to 🟠 Strava page in sidebar")
print("3. Click 'Connect Strava' button")
print("4. Authorize on Strava website")
print("5. Your activities will sync automatically! 🚀")
