"""
VH-Database Backup Manager

Provides automatic backup and restore functionality for VH-Database.db
"""

import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def backup_vh_database(source_path: Path = None, backup_dir: Path = None) -> Path:
    """
    Create a timestamped backup of VH-Database.db
    
    Args:
        source_path: Path to VH-Database.db (default: data/VH-Database.db)
        backup_dir: Backup destination (default: data/backups/)
    
    Returns:
        Path to created backup file
    """
    if source_path is None:
        source_path = Path(__file__).parent.parent / "data" / "VH-Database.db"
    
    if backup_dir is None:
        backup_dir = source_path.parent / "backups"
    
    # Ensure backup directory exists
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if source exists
    if not source_path.exists():
        logger.warning(f"VH-Database not found at {source_path}, skipping backup")
        return None
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"VH-Database_backup_{timestamp}.db"
    
    try:
        # Use SQLite backup API for consistent backup
        with sqlite3.connect(str(source_path)) as source_conn:
            with sqlite3.connect(str(backup_path)) as backup_conn:
                source_conn.backup(backup_conn)
        
        logger.info(f"✓ Backup created: {backup_path}")
        logger.info(f"  Size: {backup_path.stat().st_size / (1024*1024):.2f} MB")
        
        return backup_path
    
    except Exception as e:
        logger.error(f"✗ Backup failed: {e}")
        return None


def restore_vh_database(backup_path: Path, target_path: Path = None) -> bool:
    """
    Restore VH-Database from a backup
    
    Args:
        backup_path: Path to backup file
        target_path: Where to restore (default: data/VH-Database.db)
    
    Returns:
        True if successful, False otherwise
    """
    if target_path is None:
        target_path = Path(__file__).parent.parent / "data" / "VH-Database.db"
    
    if not backup_path.exists():
        logger.error(f"Backup file not found: {backup_path}")
        return False
    
    try:
        # Create temporary copy while restoring
        temp_path = target_path.parent / f"{target_path.name}.tmp"
        
        with sqlite3.connect(str(backup_path)) as backup_conn:
            with sqlite3.connect(str(temp_path)) as temp_conn:
                backup_conn.backup(temp_conn)
        
        # Replace original with restored
        if target_path.exists():
            target_path.unlink()
        temp_path.rename(target_path)
        
        logger.info(f"✓ Restored from: {backup_path}")
        return True
    
    except Exception as e:
        logger.error(f"✗ Restore failed: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def cleanup_old_backups(backup_dir: Path = None, keep_count: int = 10) -> int:
    """
    Remove old backups, keeping only the most recent N
    
    Args:
        backup_dir: Backup directory (default: data/backups/)
        keep_count: Number of backups to keep
    
    Returns:
        Number of backups deleted
    """
    if backup_dir is None:
        backup_dir = Path(__file__).parent.parent / "data" / "backups"
    
    if not backup_dir.exists():
        return 0
    
    # Find all VH-Database backups
    backups = sorted(
        backup_dir.glob("VH-Database_backup_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True  # Most recent first
    )
    
    # Delete old ones
    deleted_count = 0
    for backup in backups[keep_count:]:
        try:
            backup.unlink()
            logger.info(f"Deleted old backup: {backup.name}")
            deleted_count += 1
        except Exception as e:
            logger.warning(f"Failed to delete {backup.name}: {e}")
    
    return deleted_count


if __name__ == '__main__':
    # For testing
    logging.basicConfig(level=logging.INFO)
    
    print("VH-Database Backup Test")
    print("=" * 60)
    
    backup_path = backup_vh_database()
    if backup_path:
        print(f"\nBackup location: {backup_path}")
        print(f"Backup exists: {backup_path.exists()}")
    
    # Cleanup old backups
    deleted = cleanup_old_backups(keep_count=5)
    print(f"\nCleaned up {deleted} old backups")
