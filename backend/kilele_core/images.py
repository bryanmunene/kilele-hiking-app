"""Bounded, metadata-free images suitable for durable database storage."""
import base64
import io
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError


def image_data_url(data):
    if not data or len(data) > 5 * 1024 * 1024:
        raise ValueError("Choose an image smaller than 5 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.width * source.height > 20_000_000:
                    raise ValueError("Image dimensions are too large.")
                picture = ImageOps.exif_transpose(source).convert("RGB")
                picture.thumbnail((600, 600))
                output = io.BytesIO()
                picture.save(output, format="JPEG", quality=80, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise ValueError("Choose a valid JPEG, PNG or WebP image.") from None
