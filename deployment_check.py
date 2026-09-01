"""
Pre-Deployment Checklist for Kilele App
Run this to verify your app is ready for deployment
"""
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def check_file_exists(filepath, description):
    """Check if a file exists"""
    path = ROOT / filepath
    if path.exists():
        print(f"[OK] {description}")
        return True
    else:
        print(f"[FAIL] {description} - MISSING")
        return False

def check_env_variables():
    """Check if required environment variables are documented"""
    env_example = Path(".env.example")
    frontend_secrets = Path("frontend") / ".streamlit" / "secrets.toml.example"

    checks = []
    checks.append(check_file_exists(env_example, "Root .env.example"))
    checks.append(check_file_exists(frontend_secrets, "Frontend secrets.toml.example"))

    env_content = (ROOT / env_example).read_text(encoding="utf-8") if (ROOT / env_example).exists() else ""
    for key in [
        "DATABASE_URL",
        "SECRET_KEY",
        "API_BASE_URL",
        "CORS_ORIGINS",
        "STRAVA_CLIENT_ID",
        "MPESA_CONSUMER_KEY",
    ]:
        present = key in env_content
        print(f"{'[OK]' if present else '[FAIL]'} Environment docs include {key}")
        checks.append(present)

    return all(checks)

def check_requirements():
    """Check if requirements files exist"""
    backend_req = Path("backend") / "requirements.txt"
    frontend_req = Path("frontend") / "requirements.txt"

    checks = []
    checks.append(check_file_exists(backend_req, "Backend requirements.txt"))
    checks.append(check_file_exists(frontend_req, "Frontend requirements.txt"))

    requirement_checks = {
        backend_req: ["email-validator", "psycopg2-binary", "fastapi", "uvicorn"],
        frontend_req: ["psycopg2-binary", "streamlit", "sqlalchemy"],
    }
    for req_file, packages in requirement_checks.items():
        content = (ROOT / req_file).read_text(encoding="utf-8").lower() if (ROOT / req_file).exists() else ""
        for package in packages:
            present = package in content
            print(f"{'[OK]' if present else '[FAIL]'} {req_file} includes {package}")
            checks.append(present)

    return all(checks)

def check_deployment_files():
    """Check if deployment configuration files exist"""
    checks = []
    for filepath, description in [
        (Path("backend") / "Dockerfile", "Backend Dockerfile"),
        (Path("frontend") / "Dockerfile", "Frontend Dockerfile"),
        (Path("docker-compose.yml"), "Docker Compose production-like stack"),
        (Path(".dockerignore"), ".dockerignore"),
        (Path("backend") / "Procfile", "Procfile for process-based hosts"),
        (Path("backend") / "runtime.txt", "Python runtime for process-based hosts"),
        (Path("README.md"), "Current README"),
    ]:
        checks.append(check_file_exists(filepath, description))

    return all(checks)

def check_database_config():
    """Check if database is configured for production"""
    database_file = Path("backend") / "database.py"

    if check_file_exists(database_file, "Database configuration"):
        content = (ROOT / database_file).read_text(encoding="utf-8")
        has_database_url = "DATABASE_URL" in content
        has_postgres_support = "postgresql" in content.lower()
        has_url_normalization = "postgres://" in content
        checks = [has_database_url, has_postgres_support, has_url_normalization]
        print(f"{'[OK]' if has_database_url else '[FAIL]'} DATABASE_URL support detected")
        print(f"{'[OK]' if has_postgres_support else '[FAIL]'} PostgreSQL support detected")
        print(f"{'[OK]' if has_url_normalization else '[FAIL]'} postgres:// URL normalization detected")
        return all(checks)
    return False


def check_runtime_guards():
    """Check production guardrails exist."""
    config_file = Path("backend") / "config.py"
    main_file = Path("backend") / "main.py"
    checks = []
    checks.append(check_file_exists(config_file, "Backend config"))
    checks.append(check_file_exists(main_file, "Backend app entrypoint"))

    config_content = (ROOT / config_file).read_text(encoding="utf-8") if (ROOT / config_file).exists() else ""
    main_content = (ROOT / main_file).read_text(encoding="utf-8") if (ROOT / main_file).exists() else ""
    for label, present in [
        ("Production configuration validation", "production_errors" in config_content),
        ("Runtime validation call", "validate_for_runtime" in main_content),
        ("Database-backed health check", "SELECT 1" in main_content),
    ]:
        print(f"{'[OK]' if present else '[FAIL]'} {label}")
        checks.append(present)

    return all(checks)

def main():
    """Run all checks"""
    print("=" * 60)
    print("KILELE APP - PRE-DEPLOYMENT CHECKLIST")
    print("=" * 60)
    print()
    
    all_passed = True
    
    print("Checking Requirements Files...")
    all_passed = check_requirements() and all_passed
    print()
    
    print("Checking Deployment Configuration...")
    all_passed = check_deployment_files() and all_passed
    print()
    
    print("Checking Environment Configuration...")
    all_passed = check_env_variables() and all_passed
    print()
    
    print("Checking Database Configuration...")
    all_passed = check_database_config() and all_passed
    print()

    print("Checking Runtime Guardrails...")
    all_passed = check_runtime_guards() and all_passed
    print()
    
    print("=" * 60)
    if all_passed:
        print("[OK] ALL CHECKS PASSED!")
        print()
        print("Next Steps:")
        print("1. Generate SECRET_KEY: openssl rand -hex 32")
        print("2. Set DATABASE_URL to a persistent PostgreSQL database")
        print("3. Set CORS_ORIGINS to the deployed Streamlit URL")
        print("4. Deploy backend and frontend as separate services or use Docker Compose")
        print("5. Configure optional Strava, Cloudinary, M-Pesa, email, and Sentry credentials")
        print()
        print("See DEPLOYMENT.md for detailed instructions")
    else:
        print("[FAIL] SOME CHECKS FAILED")
        print("Please fix the issues above before deploying")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
