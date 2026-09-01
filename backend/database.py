from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
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


# Lightweight compatibility migrations for databases created by older releases
# or by the Streamlit service before the API service starts.
def _add_missing_columns():
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
        "achievements": {
            "requirement_type": ("string", None),
            "requirement_value": ("float", "0"),
        },
        "conversation_participants": {
            "joined_at": ("datetime", None),
            "last_read_at": ("datetime", None),
            "created_at": ("datetime", None),
        },
        "hike_sessions": {
            "completed_at": ("datetime", None),
            "ended_at": ("datetime", None),
            "is_active": ("boolean", "true"),
            "status": ("string", "'in_progress'"),
            "current_latitude": ("float", None),
            "current_longitude": ("float", None),
            "distance_covered_km": ("float", "0"),
            "duration_minutes": ("integer", "0"),
            "duration_hours": ("float", "0"),
            "elevation_gain_m": ("float", "0"),
            "route_data": ("text", None),
            "created_at": ("datetime", None),
            "rating": ("integer", None),
        },
        "messages": {
            "updated_at": ("datetime", None),
        },
        "planned_hikes": {
            "price": ("float", "0"),
            "max_participants": ("integer", None),
        },
        "reviews": {
            "photos": ("json", None),
            "trail_condition": ("string", None),
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


# Initialize database (create tables)
def init_database():
    """Create all database tables"""
    from models import user, hike, review, achievement, activity, bookmark, follow, hike_session, message, session_token
    Base.metadata.create_all(bind=engine)
    _add_missing_columns()
