from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Import config
try:
    from config import settings
    DATABASE_URL = settings.DATABASE_URL
except ImportError:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kilele.db")

# Database engine configuration
engine_kwargs = {}

if "sqlite" in DATABASE_URL:
    # SQLite specific settings
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL specific settings
    engine_kwargs["pool_pre_ping"] = True  # Verify connections before using
    engine_kwargs["pool_size"] = 10  # Connection pool size
    engine_kwargs["max_overflow"] = 20  # Max overflow connections
    engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour
    engine_kwargs["echo"] = os.getenv("DEBUG", "False").lower() == "true"

engine = create_engine(DATABASE_URL, **engine_kwargs)

# PostgreSQL optimization: Set optimal parameters
if "postgresql" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_postgres_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET timezone='Africa/Nairobi'")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for getting database session (FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Context manager for getting database session (direct use)
@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Initialize database (create tables)
def init_database():
    """Create all database tables"""
    from models import user, hike, review, achievement, activity, bookmark, follow, hike_session, message
    Base.metadata.create_all(bind=engine)
