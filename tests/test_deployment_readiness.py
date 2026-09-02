import unittest
import os
import sys
from types import SimpleNamespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"


class DeploymentReadinessTests(unittest.TestCase):
    def test_container_and_secret_templates_exist(self):
        expected_files = [
            ROOT / ".dockerignore",
            ROOT / "docker-compose.yml",
            ROOT / "backend" / "Dockerfile",
            ROOT / "frontend" / "Dockerfile",
            ROOT / "frontend" / ".streamlit" / "secrets.toml.example",
            ROOT / "render.yaml",
            ROOT / "FREE_DEPLOYMENT.md",
        ]
        for path in expected_files:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"{path} should exist")

    def test_requirements_include_production_database_support(self):
        backend_requirements = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8").lower()
        frontend_requirements = (ROOT / "frontend" / "requirements.txt").read_text(encoding="utf-8").lower()

        self.assertIn("psycopg2-binary", backend_requirements)
        self.assertIn("email-validator", backend_requirements)
        self.assertIn("cloudinary", backend_requirements)
        self.assertIn("psycopg2-binary", frontend_requirements)
        self.assertIn("cloudinary", frontend_requirements)

    def test_compose_uses_shared_postgres_database(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("postgres:16-alpine", compose)
        self.assertGreaterEqual(compose.count("postgresql://kilele:kilele@postgres:5432/kilele"), 2)
        self.assertIn("SECRET_KEY", compose)

    def test_render_blueprint_targets_free_backend_with_external_database(self):
        blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")
        self.assertIn("runtime: python", blueprint)
        self.assertIn("plan: free", blueprint)
        self.assertIn("rootDir: backend", blueprint)
        self.assertIn("healthCheckPath: /health", blueprint)
        self.assertIn("DATABASE_URL", blueprint)
        self.assertIn("sync: false", blueprint)

    def test_production_build_does_not_publish_default_credentials(self):
        forbidden = ["admin123", "password123", "demo123", "Nesh always", "permanent session"]
        scan_roots = [ROOT / "README.md", ROOT / "frontend", ROOT / "backend"]
        for root in scan_roots:
            paths = [root] if root.is_file() else root.rglob("*")
            for path in paths:
                if not path.is_file() or path.suffix.lower() not in {".py", ".md", ".example"}:
                    continue
                content = path.read_text(encoding="utf-8", errors="ignore")
                for needle in forbidden:
                    with self.subTest(path=path, needle=needle):
                        self.assertNotIn(needle, content)

    def test_core_pages_do_not_ship_placeholder_workflows(self):
        targets = [
            ROOT / "frontend" / "pages" / "12_💬_Messages.py",
            ROOT / "frontend" / "pages" / "19_🎒_Hiking_Gear.py",
            ROOT / "frontend" / "pages" / "21_🎫_Register_for_Hikes.py",
            ROOT / "frontend" / "mpesa_service.py",
        ]
        forbidden = ["Coming soon", "being migrated", "DEMO123456", "demo_mode"]
        for path in targets:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for needle in forbidden:
                with self.subTest(path=path, needle=needle):
                    self.assertNotIn(needle, content)

    def test_mpesa_checkout_requires_real_configuration(self):
        for key in [
            "MPESA_CONSUMER_KEY",
            "MPESA_CONSUMER_SECRET",
            "MPESA_PASSKEY",
            "MPESA_SHORTCODE",
        ]:
            os.environ.pop(key, None)

        sys.path.insert(0, str(FRONTEND_DIR))
        sys.modules.pop("mpesa_service", None)
        original_streamlit = sys.modules.get("streamlit")
        sys.modules["streamlit"] = SimpleNamespace(secrets={})

        try:
            import mpesa_service

            self.assertFalse(mpesa_service.is_mpesa_configured())
            result = mpesa_service.initiate_stk_push(
                "0712345678",
                100,
                "TEST-HIKE",
                "Test payment",
            )
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "M-Pesa payments are not configured yet.")
            self.assertNotIn("checkout_request_id", result)
        finally:
            sys.modules.pop("mpesa_service", None)
            if original_streamlit is None:
                sys.modules.pop("streamlit", None)
            else:
                sys.modules["streamlit"] = original_streamlit
