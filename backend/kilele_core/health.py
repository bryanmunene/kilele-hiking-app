"""Non-sensitive operational summaries and bounded provider-run records."""
from datetime import datetime, timedelta
from sqlalchemy import func, select, text
from .operations import operation_runs, outbox, reports


def record_run(db, kind, run_id, status, run_url=None):
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    if kind not in {"backup", "email_test"} or status not in {"running", "success", "failure", "cancelled"}:
        raise ValueError("Invalid operation status.")
    if not str(run_id).replace("-", "").isalnum() or len(str(run_id)) > 70:
        raise ValueError("Invalid run identifier.")
    prefix = "https://github.com/bryanmunene/kilele-hiking-app/actions/runs/"
    if run_url is not None and (not run_url.startswith(prefix) or not run_url[len(prefix):].isdigit()):
        raise ValueError("Invalid workflow link.")
    now = datetime.utcnow()
    finished = None if status == "running" else now
    insert = sqlite_insert if db.bind.dialect.name == "sqlite" else pg_insert
    statement = insert(operation_runs).values(key=f"{kind}:{run_id}", kind=kind, status=status,
        started_at=now, finished_at=finished, run_url=run_url)
    db.execute(statement.on_conflict_do_update(index_elements=[operation_runs.c.key],
        set_={"status": status, "finished_at": finished, "run_url": run_url}))


def operational_summary(db, now=None):
    now = now or datetime.utcnow()
    pending = outbox.c.sent_at.is_(None)
    row = db.execute(select(
        func.count().filter(pending).label("pending"),
        func.count().filter(pending, outbox.c.attempts >= 8).label("failed"),
        func.count().filter(outbox.c.sent_at >= now - timedelta(days=1)).label("sent_today"),
        func.min(outbox.c.created_at).filter(pending).label("oldest_pending"),
    ).select_from(outbox)).mappings().one()
    support = db.execute(select(func.count().label("open"),
        func.min(reports.c.created_at).label("oldest_open")).where(reports.c.status == "open")).mappings().one()
    backup = db.execute(select(operation_runs).where(operation_runs.c.kind == "backup").order_by(
        operation_runs.c.started_at.desc()).limit(1)).mappings().first()
    success = db.execute(select(operation_runs.c.finished_at).where(operation_runs.c.kind == "backup",
        operation_runs.c.status == "success").order_by(operation_runs.c.finished_at.desc()).limit(1)).scalar_one_or_none()
    size = None
    try:
        with db.begin_nested():
            if db.bind.dialect.name == "postgresql":
                size = db.execute(text("SELECT pg_database_size(current_database())")).scalar_one()
            elif db.bind.dialect.name == "sqlite":
                size = db.execute(text("PRAGMA page_count")).scalar_one() * db.execute(text("PRAGMA page_size")).scalar_one()
    except Exception:
        pass
    return {"mail": dict(row), "support": dict(support),
            "backup": {"latest": dict(backup) if backup else None, "last_success": success,
                       "stale": success is None or now - success > timedelta(hours=36)},
            "database_bytes": size, "checked_at": now}
