from sqlalchemy import create_engine, event, inspect, pool
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

# Lightweight local migrations for existing SQLite databases.
def _add_missing_sqlite_columns():
    if engine.dialect.name != "sqlite":
        return

    migrations = {
        "hike_sessions": {
            "ended_at": "DATETIME",
            "status": "VARCHAR(30) DEFAULT 'in_progress'",
            "duration_hours": "FLOAT DEFAULT 0",
            "elevation_gain_m": "FLOAT DEFAULT 0",
            "route_data": "TEXT",
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


# Initialize database (create tables)
def init_database():
    """Create all database tables"""
    from models import user, hike, review, achievement, activity, bookmark, follow, hike_session, message
    Base.metadata.create_all(bind=engine)
    _add_missing_sqlite_columns()
