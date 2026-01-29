"""
Unified database module for Streamlit app
SQLAlchemy with SQLite/PostgreSQL support
"""
import streamlit as st
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

# Import config
try:
    from config import settings
    DATABASE_URL = settings.DATABASE_URL
except ImportError:
    # Fallback to local SQLite
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "kilele.db")
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Database engine configuration
engine_kwargs = {}

if "sqlite" in DATABASE_URL:
    # SQLite specific settings
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["echo"] = False
else:
    # PostgreSQL specific settings (for production)
    engine_kwargs["pool_pre_ping"] = True  # Verify connections before using
    engine_kwargs["pool_size"] = 5  # Smaller pool for Streamlit
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour
    engine_kwargs["echo"] = False

# Create engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

# PostgreSQL optimization
if "postgresql" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_postgres_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET timezone='Africa/Nairobi'")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    from models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)

@st.cache_resource
def get_engine():
    """Cached database engine for Streamlit"""
    return engine
