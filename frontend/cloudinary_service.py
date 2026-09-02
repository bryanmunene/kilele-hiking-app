"""
Cloudinary image storage service for Kilele frontend
Handles profile pictures, trail images, and review photos
"""
import base64
import io
from typing import Optional, Dict

try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.utils
except ImportError:
    cloudinary = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from config import settings
    
    # Configure Cloudinary if credentials available
    if cloudinary and settings.has_cloudinary:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
except ImportError:
    pass

class CloudinaryService:
    """Cloudinary image management service for Streamlit"""
    
    def __init__(self):
        self.enabled = self._check_configured()
    
    def _check_configured(self) -> bool:
        """Check if Cloudinary is properly configured"""
        try:
            from config import settings
            return bool(cloudinary and settings.has_cloudinary)
        except:
            return False
    
    def upload_image(
        self,
        file_data,
        folder: str = "kilele",
        public_id: Optional[str] = None,
        transformation: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Upload image to Cloudinary
        
        Args:
            file_data: Streamlit UploadedFile or bytes
            folder: Cloudinary folder
            public_id: Optional custom ID
            transformation: Optional transformation parameters
            
        Returns:
            Image URL or None if upload fails
        """
        if not self.enabled:
            return None
        
        try:
            # Default transformations for optimization
            if transformation is None:
                transformation = {
                    'quality': 'auto:good',
                    'fetch_format': 'auto',
                }
            
            # Upload options
            upload_options = {
                'folder': folder,
                'resource_type': 'image',
                'transformation': transformation,
            }
            
            if public_id:
                upload_options['public_id'] = public_id
                upload_options['overwrite'] = True
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file_data, **upload_options)
            
            return result['secure_url']
            
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            return None
    
    def upload_profile_picture(self, file_data, user_id: int) -> Optional[str]:
        """Upload user profile picture - Returns URL"""
        return self.upload_image(
            file_data,
            folder="kilele/profiles",
            public_id=f"user_{user_id}",
            transformation={
                'width': 400,
                'height': 400,
                'crop': 'fill',
                'gravity': 'face',
                'quality': 'auto:good',
                'fetch_format': 'auto',
            }
        )
    
    def upload_trail_image(self, file_data, hike_id: int) -> Optional[str]:
        """Upload trail/hike image - Returns URL"""
        return self.upload_image(
            file_data,
            folder="kilele/trails",
            public_id=f"trail_{hike_id}",
            transformation={
                'width': 1200,
                'height': 800,
                'crop': 'fill',
                'quality': 'auto:good',
                'fetch_format': 'auto',
            }
        )
    
    def upload_review_photo(self, file_data, review_id: int, photo_index: int = 0) -> Optional[str]:
        """Upload review photo - Returns URL"""
        return self.upload_image(
            file_data,
            folder="kilele/reviews",
            public_id=f"review_{review_id}_{photo_index}",
            transformation={
                'width': 800,
                'height': 600,
                'crop': 'limit',
                'quality': 'auto:good',
                'fetch_format': 'auto',
            }
        )
    
    def get_optimized_url(self, url: str, width: int = 400) -> str:
        """
        Get optimized Cloudinary URL from existing URL
        Falls back to original URL if not a Cloudinary image
        """
        if not url or 'cloudinary.com' not in url:
            return url
        
        try:
            if cloudinary is None:
                return url
            # Extract public_id from URL
            parts = url.split('/')
            upload_index = parts.index('upload')
            public_id = '/'.join(parts[upload_index + 2:])
            
            # Generate optimized URL
            optimized, _ = cloudinary.utils.cloudinary_url(
                public_id,
                transformation={
                    'width': width,
                    'quality': 'auto:good',
                    'fetch_format': 'auto',
                },
                secure=True
            )
            return optimized
        except:
            return url


def uploaded_image_to_data_url(
    uploaded_file,
    *,
    max_size: tuple[int, int] = (1200, 800),
    quality: int = 82,
    max_bytes: int = 1_500_000,
) -> Optional[str]:
    """
    Convert an uploaded image to a compact data URL for free-tier durable storage.

    This is a bounded fallback for deployments without Cloudinary. Large originals
    are resized and encoded as JPEG so Neon stores only a small display image.
    """
    if Image is None:
        return None

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
        image.thumbnail(max_size)

        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        data = output.getvalue()

        if len(data) > max_bytes:
            return None

        encoded = base64.b64encode(data).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        print(f"Data URL image fallback error: {e}")
        return None

# Global instance
cloudinary_service = CloudinaryService()
