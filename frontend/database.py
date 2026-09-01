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


def normalize_database_url(url: str) -> str:
    """Normalize platform-provided database URLs for SQLAlchemy."""
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


DATABASE_URL = normalize_database_url(DATABASE_URL)

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

def _column_sql(column_type: str) -> str:
    dialect = engine.dialect.name
    type_map = {
        "boolean": "BOOLEAN",
        "datetime": "DATETIME" if dialect == "sqlite" else "TIMESTAMP",
        "float": "FLOAT",
        "integer": "INTEGER",
        "json": "JSON" if dialect == "sqlite" else "JSONB",
        "string": "VARCHAR",
        "text": "TEXT",
    }
    return type_map[column_type]


def _default_sql(default: str | None) -> str:
    if default is None:
        return ""
    return f" DEFAULT {default}"


def _add_missing_columns():
    """Apply small, backwards-compatible migrations for shared deployments."""
    migrations = {
        "users": {
            "bio": ("text", None),
            "experience_level": ("string", "'Beginner'"),
            "is_admin": ("boolean", "false"),
            "two_factor_secret": ("string", None),
            "two_factor_enabled": ("boolean", "false"),
            "two_fa_secret": ("string", None),
            "two_fa_enabled": ("boolean", "false"),
            "last_login": ("datetime", None),
        },
        "reviews": {
            "title": ("string", None),
            "difficulty_rating": ("string", None),
            "trail_condition": ("string", None),
            "conditions": ("text", None),
            "visited_date": ("datetime", None),
            "helpful_count": ("integer", "0"),
            "photos": ("json", None),
        },
        "bookmarks": {
            "notes": ("string", None),
        },
        "achievements": {
            "category": ("string", "'milestones'"),
            "requirement": ("string", None),
            "requirement_type": ("string", None),
            "requirement_value": ("float", "0"),
        },
        "user_achievements": {
            "progress": ("integer", "0"),
            "completed": ("boolean", "false"),
        },
        "conversation_participants": {
            "joined_at": ("datetime", None),
            "last_read_at": ("datetime", None),
            "created_at": ("datetime", None),
        },
        "hike_sessions": {
            "completed_at": ("datetime", None),
            "is_active": ("boolean", "true"),
            "current_latitude": ("float", None),
            "current_longitude": ("float", None),
            "distance_covered_km": ("float", "0"),
            "duration_minutes": ("integer", "0"),
            "duration_hours": ("float", "0"),
            "elevation_gain_m": ("float", "0"),
            "route_data": ("text", None),
            "rating": ("integer", None),
        },
        "messages": {
            "updated_at": ("datetime", None),
        },
        "goals": {
            "completed_at": ("datetime", None),
        },
        "planned_hikes": {
            "price": ("float", "0"),
            "max_participants": ("integer", None),
        },
    }

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table_name, columns in migrations.items():
            if table_name not in existing_tables:
                continue

            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, (column_type, default) in columns.items():
                if column_name not in existing_columns:
                    column_sql = f"{_column_sql(column_type)}{_default_sql(default)}"
                    conn.exec_driver_sql(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"
                    )


def init_database():
    """Initialize database tables and apply lightweight local migrations."""
    from models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)
    _add_missing_columns()

@st.cache_resource
def get_engine():
    """Cached database engine for Streamlit"""
    return engine
