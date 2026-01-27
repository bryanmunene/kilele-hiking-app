"""
Pre-Deployment Checklist for Kilele App
Run this to verify your app is ready for deployment
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - MISSING")
        return False

def check_env_variables():
    """Check if required environment variables are documented"""
    backend_env = os.path.join("backend", ".env.example")
    frontend_secrets = os.path.join("frontend", ".streamlit", "secrets.toml")
    
    checks = []
    checks.append(check_file_exists(backend_env, "Backend .env.example"))
    checks.append(check_file_exists(frontend_secrets, "Frontend secrets.toml template"))
    
    return all(checks)

def check_requirements():
    """Check if requirements files exist"""
    backend_req = os.path.join("backend", "requirements.txt")
    frontend_req = os.path.join("frontend", "requirements.txt")
    
    checks = []
    checks.append(check_file_exists(backend_req, "Backend requirements.txt"))
    checks.append(check_file_exists(frontend_req, "Frontend requirements.txt"))
    
    return all(checks)

def check_deployment_files():
    """Check if deployment configuration files exist"""
    procfile = os.path.join("backend", "Procfile")
    runtime = os.path.join("backend", "runtime.txt")
    gitignore = ".gitignore"
    deployment_guide = "DEPLOYMENT.md"
    
    checks = []
    checks.append(check_file_exists(procfile, "Procfile (for Heroku/Railway)"))
    checks.append(check_file_exists(runtime, "runtime.txt (Python version)"))
    checks.append(check_file_exists(gitignore, ".gitignore"))
    checks.append(check_file_exists(deployment_guide, "DEPLOYMENT.md guide"))
    
    return all(checks)

def check_database_config():
    """Check if database is configured for production"""
    database_file = os.path.join("backend", "database.py")
    
    if check_file_exists(database_file, "Database configuration"):
        with open(database_file, 'r') as f:
            content = f.read()
            if 'DATABASE_URL' in content and 'postgresql' in content.lower():
                print("   ℹ️  PostgreSQL support detected")
                return True
            else:
                print("   ⚠️  Make sure DATABASE_URL supports PostgreSQL")
                return True
    return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("🚀 KILELE APP - PRE-DEPLOYMENT CHECKLIST")
    print("=" * 60)
    print()
    
    all_passed = True
    
    print("📦 Checking Requirements Files...")
    all_passed = check_requirements() and all_passed
    print()
    
    print("🔧 Checking Deployment Configuration...")
    all_passed = check_deployment_files() and all_passed
    print()
    
    print("🔐 Checking Environment Configuration...")
    all_passed = check_env_variables() and all_passed
    print()
    
    print("🗄️  Checking Database Configuration...")
    all_passed = check_database_config() and all_passed
    print()
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("🎯 Next Steps:")
        print("1. Update backend/.env.example with production values")
        print("2. Update frontend/.streamlit/secrets.toml with backend URL")
        print("3. Generate SECRET_KEY: openssl rand -hex 32")
        print("4. Push to GitHub")
        print("5. Deploy backend to Railway/Render")
        print("6. Deploy frontend to Streamlit Cloud")
        print()
        print("📖 See DEPLOYMENT.md for detailed instructions")
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please fix the issues above before deploying")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
