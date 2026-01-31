"""
Quick setup script to verify Strava integration configuration
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔍 Checking Environment Variables...")
    
    required_vars = {
        "STRAVA_CLIENT_ID": "Strava Client ID",
        "STRAVA_CLIENT_SECRET": "Strava Client Secret"
    }
    
    optional_vars = {
        "STRAVA_REDIRECT_URI": "Redirect URI (default: http://localhost:8501/strava/callback)",
        "STRAVA_WEBHOOK_VERIFY_TOKEN": "Webhook Verify Token"
    }
    
    all_set = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value[:10]}... (set)")
        else:
            print(f"  ❌ {var}: NOT SET - {description}")
            all_set = False
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value[:30]}... (set)")
        else:
            print(f"  ⚠️  {var}: NOT SET - {description}")
    
    return all_set

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Dependencies...")
    
    packages = ["stravalib", "apscheduler", "fastapi", "sqlalchemy"]
    all_installed = True
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: installed")
        except ImportError:
            print(f"  ❌ {package}: NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_database_models():
    """Check if Strava models exist in database"""
    print("\n🗄️  Checking Database Models...")
    
    try:
        from database import SessionLocal, Base
        from models.strava import StravaToken, StravaActivity, StravaWebhookSubscription
        
        print("  ✅ StravaToken model: imported")
        print("  ✅ StravaActivity model: imported")
        print("  ✅ StravaWebhookSubscription model: imported")
        
        # Check if tables exist
        db = SessionLocal()
        try:
            token_count = db.query(StravaToken).count()
            activity_count = db.query(StravaActivity).count()
            print(f"  ℹ️  Database: {token_count} tokens, {activity_count} activities")
        except Exception as e:
            print(f"  ⚠️  Database tables may not exist: {e}")
            return False
        finally:
            db.close()
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to import models: {e}")
        return False

def check_api_routes():
    """Check if Strava routes are registered"""
    print("\n🚀 Checking API Routes...")
    
    try:
        from main import app
        
        strava_routes = [r for r in app.routes if '/strava' in str(r.path)]
        
        if strava_routes:
            print(f"  ✅ Found {len(strava_routes)} Strava routes:")
            for route in strava_routes[:5]:  # Show first 5
                print(f"     - {route.methods} {route.path}")
            if len(strava_routes) > 5:
                print(f"     ... and {len(strava_routes) - 5} more")
        else:
            print("  ❌ No Strava routes found")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to check routes: {e}")
        return False

def check_scheduler():
    """Check if scheduler can be imported"""
    print("\n⏰ Checking Scheduler...")
    
    try:
        from strava_scheduler import start_scheduler, stop_scheduler
        print("  ✅ Scheduler module: imported successfully")
        print("  ℹ️  Scheduler will start when backend runs")
        return True
    except Exception as e:
        print(f"  ❌ Failed to import scheduler: {e}")
        return False

def check_frontend_page():
    """Check if Strava frontend page exists"""
    print("\n🎨 Checking Frontend Page...")
    
    frontend_page = Path(__file__).parent / "frontend" / "pages" / "19_🟠_Strava.py"
    
    if frontend_page.exists():
        print(f"  ✅ Strava page exists: {frontend_page.name}")
        
        # Check if API_BASE_URL is configured
        content = frontend_page.read_text()
        if "API_BASE_URL" in content:
            print("  ✅ API_BASE_URL configured")
        else:
            print("  ⚠️  API_BASE_URL not found in page")
        
        return True
    else:
        print(f"  ❌ Strava page not found: {frontend_page}")
        return False

def generate_setup_commands():
    """Generate setup commands for user"""
    print("\n📋 Setup Commands:")
    print("\n1. Create Strava API App:")
    print("   Go to: https://www.strava.com/settings/api")
    print("   Create new application")
    
    print("\n2. Add to backend/.env:")
    print("   STRAVA_CLIENT_ID=your_client_id_here")
    print("   STRAVA_CLIENT_SECRET=your_client_secret_here")
    print("   STRAVA_REDIRECT_URI=http://localhost:8501/strava/callback")
    print("   STRAVA_WEBHOOK_VERIFY_TOKEN=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')")
    
    print("\n3. Install missing dependencies:")
    print("   cd backend")
    print("   pip install -r requirements.txt")
    
    print("\n4. Start backend:")
    print("   cd backend")
    print("   python main.py")
    
    print("\n5. Start frontend:")
    print("   cd frontend")
    print("   streamlit run Home.py")
    
    print("\n6. Test connection:")
    print("   - Login to Kilele app")
    print("   - Navigate to 🟠 Strava page")
    print("   - Click 'Connect Strava'")

def main():
    """Run all checks"""
    print("=" * 60)
    print("🟠 Kilele Strava Integration - Setup Check")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(backend_path)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    checks = {
        "Environment Variables": check_environment_variables(),
        "Dependencies": check_dependencies(),
        "Database Models": check_database_models(),
        "API Routes": check_api_routes(),
        "Scheduler": check_scheduler(),
        "Frontend Page": check_frontend_page()
    }
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("=" * 60)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for name, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    
    print(f"\n  {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All checks passed! Strava integration is ready.")
        print("\n📖 Next steps:")
        print("  1. Configure Strava API credentials (if not done)")
        print("  2. Start backend: cd backend && python main.py")
        print("  3. Start frontend: cd frontend && streamlit run Home.py")
        print("  4. Test connection in app")
    else:
        print("\n⚠️  Some checks failed. See details above.")
        generate_setup_commands()
    
    print("\n📚 Documentation:")
    print("  - Setup Guide: STRAVA_SETUP.md")
    print("  - Implementation Summary: STRAVA_INTEGRATION_COMPLETE.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
