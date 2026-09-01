"""
Unified database module for Streamlit app
SQLAlchemy with SQLite/PostgreSQL support
"""
import streamlit as st
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
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

def _add_missing_sqlite_columns():
    """Apply small, backwards-compatible SQLite migrations."""
    if engine.dialect.name != "sqlite":
        return

    migrations = {
        "users": {
            "bio": "TEXT",
            "experience_level": "VARCHAR DEFAULT 'Beginner'",
            "is_admin": "BOOLEAN DEFAULT 0",
            "two_factor_secret": "VARCHAR",
            "two_factor_enabled": "BOOLEAN DEFAULT 0",
        },
        "reviews": {
            "title": "VARCHAR",
            "difficulty_rating": "INTEGER",
            "trail_condition": "VARCHAR",
            "conditions": "TEXT",
            "visited_date": "DATETIME",
            "helpful_count": "INTEGER DEFAULT 0",
        },
        "bookmarks": {
            "notes": "VARCHAR(500)",
        },
        "achievements": {
            "category": "VARCHAR DEFAULT 'milestones'",
            "requirement": "VARCHAR",
            "requirement_type": "VARCHAR",
            "requirement_value": "FLOAT DEFAULT 0",
        },
        "user_achievements": {
            "progress": "INTEGER DEFAULT 0",
            "completed": "BOOLEAN DEFAULT 0",
        },
        "goals": {
            "completed_at": "DATETIME",
        },
        "planned_hikes": {
            "price": "FLOAT DEFAULT 0",
            "max_participants": "INTEGER",
        },
    }

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table_name, columns in migrations.items():
            if table_name not in existing_tables:
                continue

            existing_columns = {
                row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table_name})")
            }
            for column_name, column_sql in columns.items():
                if column_name not in existing_columns:
                    conn.exec_driver_sql(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"
                    )


def init_database():
    """Initialize database tables and apply lightweight local migrations."""
    from models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)
    _add_missing_sqlite_columns()

@st.cache_resource
def get_engine():
    """Cached database engine for Streamlit"""
    return engine
