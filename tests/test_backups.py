import importlib.util
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet, InvalidToken

spec = importlib.util.spec_from_file_location("tested_backup", Path(__file__).resolve().parents[1] / "backend" / "backup_service.py")
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class BackupTests(unittest.TestCase):
    def test_postgres_restore_removes_only_an_empty_default_schema(self):
        key = Fernet.generate_key()
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"BACKUP_ENCRYPTION_KEY": key.decode()}):
            artifact = Path(folder) / "backup.enc"
            artifact.write_bytes(Fernet(key).encrypt(b"postgres\ncustom-format-test"))
            service = backup.BackupService("postgresql://source/source", folder)
            engine = MagicMock()
            connection = engine.begin.return_value.__enter__.return_value
            inspector = MagicMock()
            with patch.object(backup, "create_engine", return_value=engine), patch.object(backup, "inspect", return_value=inspector), patch.object(backup, "run_pg") as restore:
                inspector.get_table_names.return_value = ["users"]
                with self.assertRaises(ValueError):
                    service.restore_backup(artifact, "postgresql://target/empty")
                connection.exec_driver_sql.assert_not_called()
                restore.assert_not_called()
                inspector.get_table_names.return_value = []
                service.restore_backup(artifact, "postgresql://target/empty")
                connection.exec_driver_sql.assert_called_once_with("DROP SCHEMA IF EXISTS public")
                restore.assert_called_once()
                self.assertIn("--single-transaction", restore.call_args.args[1])

    def test_encrypted_snapshot_restores_configured_sqlite_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "named-source.db"
            with closing(sqlite3.connect(source)) as db:
                db.execute("CREATE TABLE marker (value TEXT)")
                db.execute("INSERT INTO marker VALUES ('private test record')")
                db.commit()
            service = backup.BackupService("sqlite:///" + source.as_posix(), root / "backups")
            with patch.dict(os.environ, {"BACKUP_ENCRYPTION_KEY": Fernet.generate_key().decode()}):
                path = service.create_backup()
                self.assertNotIn(b"private test record", Path(path).read_bytes())
                target = root / "restored.db"
                service.restore_backup(path, "sqlite:///" + target.as_posix())
                with closing(sqlite3.connect(target)) as db:
                    self.assertEqual(db.execute("SELECT value FROM marker").fetchone()[0], "private test record")
                with self.assertRaises(ValueError):
                    service.restore_backup(path, "sqlite:///" + source.as_posix())
                with self.assertRaises(ValueError):
                    service.restore_backup(path, "sqlite:///" + target.as_posix())
            with patch.dict(os.environ, {"BACKUP_ENCRYPTION_KEY": Fernet.generate_key().decode()}):
                with self.assertRaises(InvalidToken):
                    service.restore_backup(path, "sqlite:///" + (root / "wrong-key.db").as_posix())

    def test_failed_postgres_dump_does_not_produce_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            service = backup.BackupService("postgresql://test:secret@localhost/app", folder)
            with patch.dict(os.environ, {"BACKUP_ENCRYPTION_KEY": Fernet.generate_key().decode()}), patch.object(backup, "run_pg", side_effect=RuntimeError("failure")):
                with self.assertRaises(RuntimeError):
                    service.create_backup()
            self.assertEqual(service.list_backups(), [])
