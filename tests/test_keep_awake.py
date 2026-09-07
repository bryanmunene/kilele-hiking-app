import importlib.util
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_keep_awake_module():
    module_path = ROOT / "scripts" / "keep_awake.py"
    spec = importlib.util.spec_from_file_location("keep_awake", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["keep_awake"] = module
    spec.loader.exec_module(module)
    return module


class KeepAwakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keep_awake = load_keep_awake_module()

    def test_default_endpoints_cover_streamlit_and_render(self):
        old_values = {
            key: os.environ.pop(key, None)
            for key in [
                "KILELE_FRONTEND_URL",
                "KILELE_BACKEND_HEALTH_URL",
                "KEEP_AWAKE_EXTRA_URLS",
            ]
        }
        try:
            endpoints = self.keep_awake.configured_endpoints()
        finally:
            for key, value in old_values.items():
                if value is not None:
                    os.environ[key] = value

        urls = [endpoint.url for endpoint in endpoints]

        self.assertIn(
            "https://kilele-hiking-appgit-cnrnmlnmkgku6xjzrrxzcg.streamlit.app/",
            urls,
        )
        self.assertIn(
            "https://kilele-hiking-appgit-cnrnmlnmkgku6xjzrrxzcg.streamlit.app/_stcore/health",
            urls,
        )
        self.assertIn("https://kilele-hiking-api.onrender.com/health", urls)

    def test_sleeping_or_error_pages_are_not_healthy(self):
        self.assertTrue(self.keep_awake.response_is_healthy(200, "Kilele Explorers"))
        self.assertFalse(
            self.keep_awake.response_is_healthy(
                200,
                "This app has gone to sleep due to inactivity.",
            )
        )
        self.assertFalse(self.keep_awake.response_is_healthy(500, "Kilele Explorers"))
