"""Production configuration management for Kilele backend"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kilele.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SESSION_EXPIRY_DAYS: int = int(os.getenv("SESSION_EXPIRY_DAYS", "30"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: Optional[str] = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: Optional[str] = os.getenv("CLOUDINARY_API_SECRET")
    
    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@kilele.app")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@kilele.app")
    
    # Email (SMTP alternative)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@kilele.app")
    
    # Sentry
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", "development")
    
    # API
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    CORS_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ] or ["*"]
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes", "on"}
    TIMEZONE: str = os.getenv("TIMEZONE", "Africa/Nairobi")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: int = int(os.getenv("RATE_LIMIT_LOGIN", "5"))
    RATE_LIMIT_API: int = int(os.getenv("RATE_LIMIT_API", "60"))
    RATE_LIMIT_UPLOAD: int = int(os.getenv("RATE_LIMIT_UPLOAD", "10"))
    
    # AWS (for backups)
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BACKUP_BUCKET: Optional[str] = os.getenv("AWS_BACKUP_BUCKET")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Feature Flags
    ENABLE_2FA: bool = os.getenv("ENABLE_2FA", "True").lower() == "true"
    ENABLE_WEARABLES: bool = os.getenv("ENABLE_WEARABLES", "True").lower() == "true"
    ENABLE_SOCIAL: bool = os.getenv("ENABLE_SOCIAL", "True").lower() == "true"
    ENABLE_MESSAGING: bool = os.getenv("ENABLE_MESSAGING", "True").lower() == "true"
    ENABLE_ACHIEVEMENTS: bool = os.getenv("ENABLE_ACHIEVEMENTS", "True").lower() == "true"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def use_postgresql(self) -> bool:
        """Check if using PostgreSQL"""
        return self.DATABASE_URL.startswith(("postgresql", "postgres://"))
    
    @property
    def has_cloudinary(self) -> bool:
        """Check if Cloudinary is configured"""
        return all([
            self.CLOUDINARY_CLOUD_NAME,
            self.CLOUDINARY_API_KEY,
            self.CLOUDINARY_API_SECRET
        ])
    
    @property
    def has_email(self) -> bool:
        """Check if email service is configured"""
        return bool(self.SENDGRID_API_KEY) or all([
            self.SMTP_HOST,
            self.SMTP_USER,
            self.SMTP_PASSWORD
        ])
    
    @property
    def has_sentry(self) -> bool:
        """Check if Sentry is configured"""
        return bool(self.SENTRY_DSN)

    def production_errors(self) -> list[str]:
        """Return configuration problems that should block production startup."""
        if not self.is_production:
            return []

        errors = []
        unsafe_secret_values = {
            "",
            "dev-secret-key-change-in-production",
            "your-secret-key-change-this-in-production",
            "your-secret-key-here-change-this-in-production",
        }
        if self.SECRET_KEY in unsafe_secret_values or len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be set to a unique value of at least 32 characters.")
        if self.DEBUG:
            errors.append("DEBUG must be False when ENVIRONMENT=production.")
        if self.CORS_ORIGINS == ["*"]:
            errors.append("CORS_ORIGINS must list explicit frontend origins in production.")
        if self.DATABASE_URL.startswith("sqlite") and os.getenv("ALLOW_SQLITE_IN_PRODUCTION", "").lower() not in {"1", "true", "yes"}:
            errors.append("DATABASE_URL should point to PostgreSQL in production, or set ALLOW_SQLITE_IN_PRODUCTION=true knowingly.")
        return errors

    def validate_for_runtime(self) -> None:
        """Fail fast on unsafe production settings."""
        errors = self.production_errors()
        if errors:
            raise RuntimeError("Invalid production configuration: " + " ".join(errors))

# Global settings instance
settings = Settings()
