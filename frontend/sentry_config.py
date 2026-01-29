"""
Sentry error tracking integration for Kilele frontend
"""
import sentry_sdk

try:
    from config import settings
    
    if settings.has_sentry:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=0.1,  # Lower for Streamlit
            send_default_pii=False,
        )
        print(f"✅ Sentry initialized ({settings.ENVIRONMENT})")
except Exception as e:
    print(f"⚠️ Sentry not configured: {e}")
