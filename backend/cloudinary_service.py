"""
Cloudinary image storage service for Kilele
Handles profile pictures, trail images, and review photos
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict
import os
from io import BytesIO

try:
    from config import settings
    
    # Configure Cloudinary if credentials available
    if settings.has_cloudinary:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
except ImportError:
    pass

class CloudinaryService:
    """Cloudinary image management service"""
    
    def __init__(self):
        self.enabled = self._check_configured()
    
    def _check_configured(self) -> bool:
        """Check if Cloudinary is properly configured"""
        try:
            from config import settings
            return settings.has_cloudinary
        except:
            return False
    
    def upload_image(
        self,
        file_data,
        folder: str = "kilele",
        public_id: Optional[str] = None,
        transformation: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Upload image to Cloudinary
        
        Args:
            file_data: File object, bytes, or path to file
            folder: Cloudinary folder (e.g., 'kilele/profiles', 'kilele/trails')
            public_id: Optional custom ID for the image
            transformation: Optional transformation parameters
            
        Returns:
            Dict with 'url' and 'public_id' or None if upload fails
        """
        if not self.enabled:
            print("⚠️ Cloudinary not configured, skipping upload")
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
            
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format'),
                'bytes': result.get('bytes'),
            }
            
        except Exception as e:
            print(f"❌ Cloudinary upload error: {e}")
            return None
    
    def upload_profile_picture(self, file_data, user_id: int) -> Optional[str]:
        """
        Upload user profile picture
        Returns: URL or None
        """
        result = self.upload_image(
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
        return result['url'] if result else None
    
    def upload_trail_image(self, file_data, hike_id: int) -> Optional[str]:
        """
        Upload trail/hike image
        Returns: URL or None
        """
        result = self.upload_image(
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
        return result['url'] if result else None
    
    def upload_review_photo(self, file_data, review_id: int, photo_index: int = 0) -> Optional[str]:
        """
        Upload review photo
        Returns: URL or None
        """
        result = self.upload_image(
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
        return result['url'] if result else None
    
    def delete_image(self, public_id: str) -> bool:
        """
        Delete image from Cloudinary
        
        Args:
            public_id: The Cloudinary public ID of the image
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"❌ Cloudinary delete error: {e}")
            return False
    
    def get_image_url(
        self,
        public_id: str,
        transformation: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Get optimized URL for an existing Cloudinary image
        
        Args:
            public_id: The Cloudinary public ID
            transformation: Optional transformation parameters
            
        Returns:
            Optimized image URL or None
        """
        if not self.enabled:
            return None
        
        try:
            if transformation:
                url, _ = cloudinary.utils.cloudinary_url(
                    public_id,
                    transformation=transformation,
                    secure=True
                )
                return url
            else:
                return cloudinary.CloudinaryImage(public_id).build_url(secure=True)
        except Exception as e:
            print(f"❌ Error getting Cloudinary URL: {e}")
            return None
    
    def get_thumbnail_url(self, public_id: str, size: int = 150) -> Optional[str]:
        """Get thumbnail URL for an image"""
        return self.get_image_url(
            public_id,
            transformation={
                'width': size,
                'height': size,
                'crop': 'fill',
                'quality': 'auto:low',
                'fetch_format': 'auto',
            }
        )

# Global instance
cloudinary_service = CloudinaryService()
