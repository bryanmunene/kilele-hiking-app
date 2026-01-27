"""
Unified database module for Streamlit app
SQLAlchemy with SQLite for all data operations
"""
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "kilele.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)

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
