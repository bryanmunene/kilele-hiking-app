import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class NavigationTests(unittest.TestCase):
    def test_every_existing_page_has_a_stable_registered_route(self):
        spec = importlib.util.spec_from_file_location("test_navigation_registry", ROOT / "frontend/navigation.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        paths = {entry[0] for rows in module.GROUPS.values() for entry in rows}
        legacy = {"pages/" + p.name for p in (ROOT / "frontend/pages").glob("*.py")}
        self.assertTrue(legacy <= paths)
        self.assertTrue(all((ROOT / "frontend" / p).is_file() for p in paths))
        routes = [entry[2] for rows in module.GROUPS.values() for entry in rows]
        self.assertEqual(len(routes), len(set(routes)))
        with patch.object(module.st, "Page", side_effect=lambda path, **kw: {"path": path, **kw}):
            anonymous = module.page_groups(False)
            admin = module.page_groups(True)
        self.assertTrue(all(p["visibility"] == "hidden" for p in anonymous["Organizer"]))
        self.assertTrue(all(p["visibility"] == "visible" for p in admin["Organizer"]))
        self.assertEqual(sum(p["default"] for rows in anonymous.values() for p in rows if "default" in p), 1)

    def test_slow_api_failure_has_a_bounded_wait_and_safe_message(self):
        import requests
        spec = importlib.util.spec_from_file_location("test_api_adapter", ROOT / "frontend/api_client.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(module.requests, "request", side_effect=requests.Timeout("private provider details")) as send:
            result = module.api_request("GET", "/api/v1/admin/operations")
        self.assertIn("try again", result["error"].lower())
        self.assertNotIn("private provider", result["error"])
        self.assertEqual(send.call_args.kwargs["timeout"], (10, 60))
