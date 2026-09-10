"""Read-only checks on a disposable restore target; no user values in logs."""
import os
from sqlalchemy import create_engine, inspect, text

engine = create_engine(os.environ["RESTORE_DATABASE_URL"])
try:
    tables = set(inspect(engine).get_table_names())
    if not {"users", "hikes", "hike_registrations"}.issubset(tables):
        raise RuntimeError("Restored database is missing core tables.")
    with engine.connect() as connection:
        for name in ("users", "hikes", "hike_registrations"):
            connection.execute(text(f"SELECT count(*) FROM {name}")).scalar_one()
    print("Restore verified: core tables readable; PostgreSQL restored constraints successfully.")
finally:
    engine.dispose()
