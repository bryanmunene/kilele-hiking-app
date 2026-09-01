import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"


def clear_backend_modules():
    for module_name in [
        "auth",
        "config",
        "database",
        "main",
        "models",
        "rate_limiter",
        "strava_service",
    ]:
        sys.modules.pop(module_name, None)
    for module_name in list(sys.modules):
        if module_name.startswith(("models.", "routers.", "schemas.")):
            sys.modules.pop(module_name, None)


class BackendImportTests(unittest.TestCase):
    def test_app_imports_without_optional_integrations_installed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            database_path = Path(tmpdir) / "backend-test.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
            os.environ["ENVIRONMENT"] = "development"
            os.environ["DEBUG"] = "False"
            sys.path.insert(0, str(BACKEND_DIR))
            clear_backend_modules()

            try:
                import main
                from sqlalchemy.orm import configure_mappers

                configure_mappers()

                route_paths = {route.path for route in main.app.routes}
                self.assertIn("/health", route_paths)
                self.assertIn("/api/status", route_paths)
                self.assertTrue(any(path.startswith("/api/v1/hikes") for path in route_paths))
            finally:
                loaded_main = sys.modules.get("main")
                if loaded_main and hasattr(loaded_main, "engine"):
                    loaded_main.engine.dispose()

    def test_strava_endpoints_accept_streamlit_session_tokens(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            database_path = Path(tmpdir) / "backend-session-token-test.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
            os.environ["ENVIRONMENT"] = "development"
            os.environ["DEBUG"] = "False"
            sys.path.insert(0, str(BACKEND_DIR))
            clear_backend_modules()

            try:
                import main
                from auth import _get_user_from_session_token
                from database import SessionLocal
                from fastapi import HTTPException
                from models.session_token import SessionToken
                from models.user import User

                db = SessionLocal()
                try:
                    user = User(
                        username="sessionuser",
                        email="session@example.com",
                        full_name="Session User",
                        hashed_password="unused",
                    )
                    db.add(user)
                    db.flush()
                    db.add(
                        SessionToken(
                            user_id=user.id,
                            token="streamlit-session-token",
                            expires_at=datetime.utcnow() + timedelta(days=1),
                        )
                    )
                    db.commit()

                    authenticated_user = _get_user_from_session_token("streamlit-session-token", db)
                    self.assertEqual(authenticated_user.username, "sessionuser")

                    with self.assertRaises(HTTPException):
                        _get_user_from_session_token("missing-token", db)
                finally:
                    db.close()
            finally:
                loaded_main = sys.modules.get("main")
                if loaded_main and hasattr(loaded_main, "engine"):
                    loaded_main.engine.dispose()
