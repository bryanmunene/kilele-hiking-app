import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"


class BackendImportTests(unittest.TestCase):
    def test_app_imports_without_optional_integrations_installed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            database_path = Path(tmpdir) / "backend-test.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
            os.environ["DEBUG"] = "False"
            sys.path.insert(0, str(BACKEND_DIR))
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
