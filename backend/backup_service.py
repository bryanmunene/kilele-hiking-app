"""Encrypted database snapshots with fail-closed restore to an empty target."""
import argparse
import os
import shutil
import sqlite3
import subprocess
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url

MAX_BACKUP_BYTES = 256 * 1024 * 1024


def pg_environment(database_url):
    url = make_url(database_url.replace("postgres://", "postgresql://", 1))
    env = os.environ.copy()
    env.update(PGHOST=url.host or "localhost", PGPORT=str(url.port or 5432),
        PGDATABASE=url.database or "postgres", PGUSER=url.username or "postgres",
        PGPASSWORD=url.password or "", PGCONNECT_TIMEOUT="30",
        PGSSLMODE=url.query.get("sslmode", "require"))
    return env


def run_pg(tool, args, url, **kwargs):
    command = [tool, *args]
    if os.getenv("PG_TOOLS_DOCKER") == "1":
        command = ["docker", "run", "--rm", "-i", "--network", "host",
            *[part for key in ("PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD", "PGCONNECT_TIMEOUT", "PGSSLMODE")
              for part in ("-e", key)], "postgres:18", *command]
    result = subprocess.run(command, env=pg_environment(url), stderr=subprocess.PIPE,
        timeout=600, **kwargs)
    if result.returncode:
        # stderr may contain connection strings or values from database records.
        error = result.stderr.decode("utf-8", errors="replace") if isinstance(result.stderr, bytes) else (result.stderr or "")
        reason = "provider or archive error"
        if 'schema "public" already exists' in error:
            reason = "default public schema already exists"
        elif "unrecognized configuration parameter" in error:
            reason = "incompatible PostgreSQL configuration parameter"
        elif "does not exist" in error and "role" in error:
            reason = "archive references a provider-specific database role"
        elif "unsupported version" in error:
            reason = "archive requires newer PostgreSQL tools"
        elif "Connection refused" in error or "could not connect" in error:
            reason = "restore target connection unavailable"
        raise RuntimeError(f"{tool} failed: {reason}; no successful backup/restore was recorded.")


class BackupService:
    def __init__(self, database_url=None, backup_dir=None):
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        self.backup_dir = Path(backup_dir or os.environ.get("BACKUP_DIR", "backups")).resolve()

    def _cipher(self):
        key = os.environ.get("BACKUP_ENCRYPTION_KEY")
        if not key:
            raise ValueError("BACKUP_ENCRYPTION_KEY is required. Never commit it.")
        return Fernet(key.encode())

    def create_backup(self, compress=True):
        if not self.database_url:
            raise ValueError("DATABASE_URL is required.")
        cipher = self._cipher()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        url = make_url(self.database_url)
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary) / "snapshot"
            if url.get_backend_name() == "sqlite":
                source = Path(url.database).resolve()
                if not source.is_file():
                    raise FileNotFoundError("Configured SQLite database does not exist.")
                with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as origin:
                    with closing(sqlite3.connect(snapshot)) as destination:
                        origin.backup(destination)
                        if destination.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                            raise RuntimeError("SQLite integrity check failed.")
                format_name = b"sqlite\n"
            elif url.get_backend_name() in {"postgresql", "postgres"}:
                with snapshot.open("wb") as output:
                    run_pg("pg_dump", ["--format=custom", "--no-owner", "--no-acl", "--schema=public"],
                        self.database_url, stdout=output)
                format_name = b"postgres\n"
            else:
                raise ValueError("Unsupported database type.")
            if not 0 < snapshot.stat().st_size <= MAX_BACKUP_BYTES:
                raise ValueError("Snapshot is empty or exceeds the 256 MB backup limit.")
            encrypted = cipher.encrypt(format_name + snapshot.read_bytes())
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        output = self.backup_dir / f"kilele_backup_{stamp}.enc"
        staging = output.with_suffix(".partial")
        staging.write_bytes(encrypted)
        staging.replace(output)
        return str(output)

    def restore_backup(self, backup_file, target_url=None):
        if not target_url:
            raise ValueError("An explicit, empty restore target is required.")
        if self.database_url and make_url(target_url) == make_url(self.database_url):
            raise ValueError("Refusing to restore over the source database.")
        path = Path(backup_file)
        if path.stat().st_size > 2 * MAX_BACKUP_BYTES:
            raise ValueError("Backup is too large.")
        plaintext = self._cipher().decrypt(path.read_bytes())
        format_name, content = plaintext.split(b"\n", 1)
        target = make_url(target_url)
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary) / "snapshot"
            snapshot.write_bytes(content)
            if format_name == b"sqlite" and target.get_backend_name() == "sqlite":
                destination = Path(target.database).resolve()
                if destination.exists():
                    raise ValueError("SQLite restore target must not exist.")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with closing(sqlite3.connect(snapshot)) as source:
                    if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("Backup integrity check failed.")
                shutil.copy2(snapshot, destination)
            elif format_name == b"postgres" and target.get_backend_name() == "postgresql":
                engine = create_engine(target_url)
                try:
                    if inspect(engine).get_table_names(schema="public"):
                        raise ValueError("PostgreSQL restore target must be empty.")
                finally:
                    engine.dispose()
                with snapshot.open("rb") as source:
                    run_pg("pg_restore", ["--exit-on-error", "--single-transaction", "--no-owner", "--no-acl",
                        "--dbname", target.database], target_url, stdin=source, stdout=subprocess.DEVNULL)
            else:
                raise ValueError("Backup and restore database types do not match.")
        return target_url

    def list_backups(self):
        return [str(path) for path in sorted(self.backup_dir.glob("kilele_backup_*.enc"), reverse=True)]


backup_service = BackupService()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["create", "restore", "list"])
    parser.add_argument("--file")
    parser.add_argument("--target-env", default="RESTORE_DATABASE_URL")
    args = parser.parse_args()
    try:
        if args.action == "create":
            print(backup_service.create_backup())
        elif args.action == "restore":
            backup_service.restore_backup(args.file, os.environ.get(args.target_env))
            print("Restore completed into the explicitly configured empty target.")
        else:
            print("\n".join(backup_service.list_backups()))
    except Exception as exc:
        # Never print provider errors, secrets, decrypted contents or connection URLs.
        print(f"Backup operation failed ({type(exc).__name__}). Check configuration and target.")
        if isinstance(exc, RuntimeError):
            print(str(exc))
        raise SystemExit(1)
