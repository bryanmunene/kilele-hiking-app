"""Serialize startup migrations across the website and API processes."""
from contextlib import contextmanager
from sqlalchemy import inspect, text


@contextmanager
def migration_lock(engine):
    # Transaction-level locks also work through Neon's transaction pooler.
    with engine.begin() as connection:
        if engine.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_xact_lock(7264531201)"))
        yield


def allow_unlinked_activities(engine):
    if engine.dialect.name != "postgresql":
        return
    inspector = inspect(engine)
    if "hike_sessions" not in inspector.get_table_names():
        return
    column = next(c for c in inspector.get_columns("hike_sessions") if c["name"] == "hike_id")
    if not column["nullable"]:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE hike_sessions ALTER COLUMN hike_id DROP NOT NULL"))
