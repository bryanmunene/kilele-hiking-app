import io
import sys
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"


class ImageFallbackTests(unittest.TestCase):
    def test_uploaded_image_to_data_url_resizes_and_encodes_image(self):
        sys.path.insert(0, str(FRONTEND_DIR))
        sys.modules.pop("cloudinary_service", None)

        try:
            from cloudinary_service import uploaded_image_to_data_url

            source = io.BytesIO()
            Image.new("RGB", (1600, 1000), color=(45, 120, 80)).save(source, format="PNG")
            source.seek(0)
            source.name = "trail.png"

            data_url = uploaded_image_to_data_url(
                source,
                max_size=(400, 300),
                quality=80,
                max_bytes=200_000,
            )

            self.assertIsNotNone(data_url)
            self.assertTrue(data_url.startswith("data:image/jpeg;base64,"))
            self.assertLess(len(data_url), 200_000)
        finally:
            sys.modules.pop("cloudinary_service", None)
