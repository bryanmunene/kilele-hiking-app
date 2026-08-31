"""Image utility functions for Kilele Project."""
import base64
import mimetypes
from pathlib import Path
import streamlit as st

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

def get_image_path(image_name: str) -> Path:
    """Get the full path to an image in the static directory"""
    normalized = image_name.replace("\\", "/")
    if normalized.startswith("/static/"):
        normalized = normalized.removeprefix("/static/")
    elif normalized.startswith("static/"):
        normalized = normalized.removeprefix("static/")
    static_root = STATIC_DIR.resolve()
    candidate = (static_root / normalized).resolve()
    try:
        candidate.relative_to(static_root)
    except ValueError:
        return static_root / "__invalid_image_path__"
    return candidate


@st.cache_data(show_spinner=False)
def image_data_url(image_name: str) -> str | None:
    """Return a local image as a browser-safe data URL."""
    if not image_name or image_name.startswith(("http://", "https://")):
        return None

    image_path = get_image_path(image_name)
    if not image_path.is_file():
        return None

    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"

def display_image(image_name: str, **kwargs):
    """Display an image from the static directory
    
    Args:
        image_name: Name of the image file (e.g., 'Cover.jpg' or 'static/Cover.jpg')
        **kwargs: Additional arguments to pass to st.image()
    """
    if not image_name:
        return
    
    # Streamlit 1.62 removed use_column_width. Translate older call sites so
    # images keep rendering while the rest of the app is migrated.
    use_column_width = kwargs.pop("use_column_width", None)
    if "width" not in kwargs:
        kwargs["width"] = "stretch" if use_column_width is not False else "content"
    
    # Check if it's a URL
    if image_name.startswith('http'):
        try:
            st.image(image_name, **kwargs)
        except Exception:
            st.markdown("🏔️ 📷")
        return
    
    # Remove 'static/' prefix if present
    # Local file
    image_path = get_image_path(image_name)
    
    if image_path.exists():
        try:
            st.image(str(image_path), **kwargs)
        except Exception:
            st.caption("Image unavailable")
    else:
        st.caption("Image unavailable")

def image_exists(image_name: str) -> bool:
    """Check if an image exists in the static directory"""
    if not image_name or image_name.startswith("http"):
        return False
    return get_image_path(image_name).exists()
