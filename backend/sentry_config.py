"""
Sentry error tracking integration for Kilele backend
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

try:
    from config import settings
    
    if settings.has_sentry:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=1.0 if settings.is_development else 0.1,
            profiles_sample_rate=1.0 if settings.is_development else 0.1,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            send_default_pii=False,  # Don't send personally identifiable information
        )
        print(f"✅ Sentry initialized ({settings.SENTRY_ENVIRONMENT})")
except Exception as e:
    print(f"⚠️ Sentry not configured: {e}")
