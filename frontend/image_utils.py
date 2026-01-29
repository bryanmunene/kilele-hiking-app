"""Image utility functions for Kilele Project"""
import os
from pathlib import Path
import streamlit as st
from PIL import Image

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

def get_image_path(image_name: str) -> Path:
    """Get the full path to an image in the static directory"""
    return STATIC_DIR / image_name

def display_image(image_name: str, **kwargs):
    """Display an image from the static directory
    
    Args:
        image_name: Name of the image file (e.g., 'Cover.jpg' or 'static/Cover.jpg')
        **kwargs: Additional arguments to pass to st.image()
    """
    if not image_name:
        return
    
    # Set mobile-responsive default if width not specified
    if 'width' not in kwargs and 'use_column_width' not in kwargs:
        kwargs['use_column_width'] = True
    
    # Check if it's a URL
    if image_name.startswith('http'):
        try:
            st.image(image_name, **kwargs)
        except Exception:
            st.markdown("🏔️ 📷")
        return
    
    # Remove 'static/' prefix if present
    if image_name.startswith('static/'):
        image_name = image_name.replace('static/', '', 1)
    
    # Local file
    image_path = get_image_path(image_name)
    
    if image_path.exists():
        try:
            st.image(str(image_path), **kwargs)
        except Exception as e:
            # Fallback to emoji if image fails to load
            st.markdown("🏔️ 📷")
    else:
        # Image doesn't exist, show placeholder
        st.markdown("🏔️ 📷")

def image_exists(image_name: str) -> bool:
    """Check if an image exists in the static directory"""
    if not image_name or image_name.startswith('http'):
        return False
    return get_image_path(image_name).exists()
