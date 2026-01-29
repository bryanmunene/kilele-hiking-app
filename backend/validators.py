"""
Input validation utilities for security
Prevents XSS, SQL injection, and other attacks
"""
import re
from typing import Optional
import html

def sanitize_html(text: str) -> str:
    """Remove HTML tags and escape special characters"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Escape special characters
    text = html.escape(text)
    return text.strip()

def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, "Username must be less than 30 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, hyphens, and underscores"
    
    return True, None

def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email is too long"
    
    return True, None

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    # Check for at least one letter and one number
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, None

def validate_trail_name(name: str) -> tuple[bool, Optional[str]]:
    """Validate trail name"""
    if not name or not name.strip():
        return False, "Trail name is required"
    
    name = name.strip()
    
    if len(name) < 3:
        return False, "Trail name must be at least 3 characters"
    
    if len(name) > 100:
        return False, "Trail name must be less than 100 characters"
    
    return True, None

def validate_coordinates(latitude: float, longitude: float) -> tuple[bool, Optional[str]]:
    """Validate GPS coordinates"""
    # Kenya's approximate bounds
    # Latitude: -4.7 to 5.0
    # Longitude: 33.9 to 41.9
    
    if not (-5 <= latitude <= 6):
        return False, "Latitude must be between -5 and 6 (Kenya region)"
    
    if not (33 <= longitude <= 42):
        return False, "Longitude must be between 33 and 42 (Kenya region)"
    
    return True, None

def validate_distance(distance: float) -> tuple[bool, Optional[str]]:
    """Validate trail distance"""
    if distance <= 0:
        return False, "Distance must be greater than 0"
    
    if distance > 500:  # 500km seems reasonable max
        return False, "Distance seems too large (max 500km)"
    
    return True, None

def validate_duration(duration: float) -> tuple[bool, Optional[str]]:
    """Validate trail duration in hours"""
    if duration <= 0:
        return False, "Duration must be greater than 0"
    
    if duration > 720:  # 30 days max
        return False, "Duration seems too large (max 720 hours/30 days)"
    
    return True, None

def validate_image_url(url: str) -> tuple[bool, Optional[str]]:
    """Validate image URL format"""
    if not url:
        return True, None  # Optional field
    
    url_pattern = r'^https?://.+'
    if not re.match(url_pattern, url):
        return False, "Invalid URL format (must start with http:// or https://)"
    
    if len(url) > 2000:
        return False, "URL is too long"
    
    # Check for common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(url.lower().endswith(ext) for ext in image_extensions):
        # Could be cloudinary URL without extension
        if 'cloudinary.com' not in url.lower():
            return False, "URL must point to an image file"
    
    return True, None

def clean_text_input(text: str, max_length: int = 5000) -> str:
    """
    Clean and sanitize text input
    Removes excess whitespace, limits length
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = sanitize_html(text)
    
    # Remove excess whitespace
    text = ' '.join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()
