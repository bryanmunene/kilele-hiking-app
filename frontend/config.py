"""Production configuration management for Kilele frontend"""
import os
from typing import Optional

class Settings:
    """Application settings from environment variables or Streamlit secrets"""
    
    def __init__(self):
        # Try to get from Streamlit secrets first, fallback to env vars
        try:
            import streamlit as st
            self._secrets = st.secrets
        except:
            self._secrets = None
    
    def _get(self, key: str, default: any = None) -> any:
        """Get value from secrets or environment"""
        if self._secrets and key in self._secrets:
            return self._secrets[key]
        return os.getenv(key, default)
    
    @property
    def DATABASE_URL(self) -> str:
        """Database connection URL"""
        return self._get("DATABASE_URL", "sqlite:///./kilele.db")
    
    @property
    def API_BASE_URL(self) -> str:
        """Backend API URL"""
        return self._get("API_BASE_URL", "http://localhost:8000")
    
    @property
    def CLOUDINARY_CLOUD_NAME(self) -> Optional[str]:
        return self._get("CLOUDINARY_CLOUD_NAME")
    
    @property
    def CLOUDINARY_API_KEY(self) -> Optional[str]:
        return self._get("CLOUDINARY_API_KEY")
    
    @property
    def CLOUDINARY_API_SECRET(self) -> Optional[str]:
        return self._get("CLOUDINARY_API_SECRET")
    
    @property
    def SENTRY_DSN(self) -> Optional[str]:
        return self._get("SENTRY_DSN")
    
    @property
    def ENVIRONMENT(self) -> str:
        return self._get("ENVIRONMENT", "development")
    
    @property
    def DEBUG(self) -> bool:
        return self._get("DEBUG", "True").lower() == "true"
    
    @property
    def MAX_UPLOAD_SIZE_MB(self) -> int:
        return int(self._get("MAX_UPLOAD_SIZE_MB", "10"))
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    @property
    def use_postgresql(self) -> bool:
        """Check if using PostgreSQL"""
        return self.DATABASE_URL.startswith("postgresql")
    
    @property
    def has_cloudinary(self) -> bool:
        """Check if Cloudinary is configured"""
        return all([
            self.CLOUDINARY_CLOUD_NAME,
            self.CLOUDINARY_API_KEY,
            self.CLOUDINARY_API_SECRET
        ])
    
    @property
    def has_sentry(self) -> bool:
        """Check if Sentry is configured"""
        return bool(self.SENTRY_DSN)

# Global settings instance
settings = Settings()
