import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
