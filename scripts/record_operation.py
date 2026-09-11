"""Record only workflow status in Neon; never log credentials or user data."""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from kilele_core.operations import operation_runs
from kilele_core.health import record_run


def main():
    run_id = os.environ["GITHUB_RUN_ID"]
    status = sys.argv[1]
    engine = create_engine(os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1))
    try:
        operation_runs.create(engine, checkfirst=True)
        with Session(engine) as db:
            record_run(db, "backup", run_id, status,
                f"https://github.com/bryanmunene/kilele-hiking-app/actions/runs/{run_id}")
            db.commit()
        print("Backup operation status recorded.")
    except Exception:
        raise SystemExit("Could not record backup status. Check connectivity and workflow logs.") from None
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
