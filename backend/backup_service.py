"""
Database backup utility for Kilele
Supports local and S3 backups
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path
import gzip
import shutil

try:
    from config import settings
except ImportError:
    settings = None

class BackupService:
    """Database backup and recovery service"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, compress: bool = True) -> str:
        """
        Create database backup
        
        Args:
            compress: Whether to gzip the backup
            
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if settings and settings.use_postgresql:
            return self._backup_postgres(timestamp, compress)
        else:
            return self._backup_sqlite(timestamp, compress)
    
    def _backup_postgres(self, timestamp: str, compress: bool) -> str:
        """Backup PostgreSQL database using pg_dump"""
        filename = f"kilele_backup_{timestamp}.sql"
        if compress:
            filename += ".gz"
        
        backup_path = self.backup_dir / filename
        
        try:
            # Use pg_dump
            dump_cmd = f'pg_dump {settings.DATABASE_URL}'
            
            if compress:
                # Pipe to gzip
                with open(backup_path, 'wb') as f:
                    process = subprocess.Popen(
                        dump_cmd,
                        shell=True,
                        stdout=subprocess.PIPE
                    )
                    compressed = gzip.compress(process.stdout.read())
                    f.write(compressed)
            else:
                # Direct dump
                with open(backup_path, 'w') as f:
                    subprocess.run(
                        dump_cmd,
                        shell=True,
                        stdout=f,
                        check=True
                    )
            
            print(f"✅ PostgreSQL backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ PostgreSQL backup failed: {e}")
            raise
    
    def _backup_sqlite(self, timestamp: str, compress: bool) -> str:
        """Backup SQLite database"""
        source_db = Path("kilele.db")
        
        if not source_db.exists():
            raise FileNotFoundError("kilele.db not found")
        
        filename = f"kilele_backup_{timestamp}.db"
        backup_path = self.backup_dir / filename
        
        # Copy database file
        shutil.copy2(source_db, backup_path)
        
        if compress:
            # Compress with gzip
            compressed_path = Path(str(backup_path) + ".gz")
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            backup_path.unlink()
            backup_path = compressed_path
        
        print(f"✅ SQLite backup created: {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_file: str):
        """
        Restore database from backup
        
        Args:
            backup_file: Path to backup file
        """
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Decompress if needed
        if backup_path.suffix == '.gz':
            print("🔧 Decompressing backup...")
            decompressed_path = backup_path.with_suffix('')
            with gzip.open(backup_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            backup_path = decompressed_path
        
        if settings and settings.use_postgresql:
            self._restore_postgres(backup_path)
        else:
            self._restore_sqlite(backup_path)
    
    def _restore_postgres(self, backup_path: Path):
        """Restore PostgreSQL database"""
        try:
            print("⚠️ Warning: This will overwrite the current database!")
            
            # Use psql to restore
            restore_cmd = f'psql {settings.DATABASE_URL} < {backup_path}'
            
            subprocess.run(restore_cmd, shell=True, check=True)
            
            print(f"✅ PostgreSQL restored from: {backup_path}")
            
        except Exception as e:
            print(f"❌ PostgreSQL restore failed: {e}")
            raise
    
    def _restore_sqlite(self, backup_path: Path):
        """Restore SQLite database"""
        target_db = Path("kilele.db")
        
        # Backup current database
        if target_db.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_current = target_db.with_name(f"kilele_before_restore_{timestamp}.db")
            shutil.copy2(target_db, backup_current)
            print(f"📦 Current database backed up to: {backup_current}")
        
        # Restore from backup
        shutil.copy2(backup_path, target_db)
        print(f"✅ SQLite restored from: {backup_path}")
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = sorted(
            self.backup_dir.glob("kilele_backup_*"),
            reverse=True  # Newest first
        )
        return [str(b) for b in backups]
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """
        Remove old backups, keeping only the most recent ones
        
        Args:
            keep_count: Number of backups to keep
        """
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            to_delete = backups[keep_count:]
            for backup in to_delete:
                Path(backup).unlink()
                print(f"🗑️ Deleted old backup: {backup}")
            
            print(f"✅ Cleaned up {len(to_delete)} old backups")
    
    def upload_to_s3(self, backup_file: str):
        """
        Upload backup to S3 (requires boto3)
        
        Args:
            backup_file: Path to backup file
        """
        if not settings or not settings.AWS_BACKUP_BUCKET:
            print("⚠️ S3 backup not configured")
            return
        
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            backup_path = Path(backup_file)
            s3_key = f"kilele_backups/{backup_path.name}"
            
            s3_client.upload_file(
                str(backup_path),
                settings.AWS_BACKUP_BUCKET,
                s3_key
            )
            
            print(f"✅ Backup uploaded to S3: s3://{settings.AWS_BACKUP_BUCKET}/{s3_key}")
            
        except ImportError:
            print("❌ boto3 not installed. Install with: pip install boto3")
        except Exception as e:
            print(f"❌ S3 upload failed: {e}")

# Global instance
backup_service = BackupService()

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_service.py create       - Create new backup")
        print("  python backup_service.py list         - List all backups")
        print("  python backup_service.py restore FILE - Restore from backup")
        print("  python backup_service.py cleanup      - Remove old backups")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        backup_file = backup_service.create_backup(compress=True)
        print(f"\n📦 Backup created: {backup_file}")
        
        # Upload to S3 if configured
        backup_service.upload_to_s3(backup_file)
        
    elif command == "list":
        backups = backup_service.list_backups()
        print(f"\n📦 Available backups ({len(backups)}):")
        for backup in backups:
            size = Path(backup).stat().st_size / (1024 * 1024)
            print(f"  - {backup} ({size:.2f} MB)")
            
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Error: Specify backup file to restore")
            sys.exit(1)
        
        backup_file = sys.argv[2]
        backup_service.restore_backup(backup_file)
        
    elif command == "cleanup":
        backup_service.cleanup_old_backups(keep_count=10)
        
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
