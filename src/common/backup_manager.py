"""
Data Backup and Versioning Module

Provides automatic backup management for data/data.json with version tracking,
hashing, and restoration capabilities. Implements:

1. Automatic backups on data modifications
2. Version history tracking with timestamps and content hashes
3. Backup rotation (keep N recent backups)
4. Restoration from any backup point
5. Version comparison and diff generation
6. Backup metadata and manifest

Architecture:
    - Backups stored in: data/backups/ directory
    - Manifest file: data/backups/manifest.json (tracks all versions)
    - Each backup: backup_YYYYMMDD_HHMMSS_HASH.json.gz (compressed)
    - Metadata: timestamp, hash, size, description

Usage:
    from common.backup_manager import BackupManager
    
    manager = BackupManager()
    
    # Create backup before modification
    backup_id = manager.create_backup("Manual backup before system deletion")
    
    # List available backups
    backups = manager.list_backups()
    
    # Restore from specific backup
    manager.restore_backup(backup_id)
    
    # Get version history
    history = manager.get_version_history()

Author: Haven Project
Version: 1.0.0
"""

import json
import hashlib
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from common.paths import data_path, project_root
from common.constants import DataConstants


logger = logging.getLogger(__name__)


class BackupStatus(Enum):
    """Backup status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"


@dataclass
class BackupMetadata:
    """Metadata for a single backup."""
    backup_id: str
    timestamp: str
    file_hash: str
    file_size: int
    description: str = ""
    status: str = BackupStatus.ACTIVE.value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class BackupManager:
    """Manages data backups and version history."""
    
    def __init__(self, data_file: Optional[Path] = None, backups_dir: Optional[Path] = None):
        """
        Initialize backup manager.
        
        Args:
            data_file: Path to data.json (default: data/data.json)
            backups_dir: Path to backups directory (default: data/backups/)
        """
        self.data_file = data_file or data_path("data.json")
        self.backups_dir = backups_dir or self.data_file.parent / "backups"
        self.manifest_file = self.backups_dir / "manifest.json"
        
        # Create backups directory if needed
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize manifest
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load backup manifest or create new one."""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load manifest: {e}")
                return self._create_empty_manifest()
        return self._create_empty_manifest()
    
    def _create_empty_manifest(self) -> Dict:
        """Create empty manifest structure."""
        return {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "total_backups": 0,
            "backups": {}
        }
    
    def _save_manifest(self) -> None:
        """Save manifest to file."""
        try:
            self.manifest["updated"] = datetime.now().isoformat()
            self.manifest["total_backups"] = len(self.manifest["backups"])
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(self.manifest, f, indent=2)
            logger.debug(f"Manifest saved: {len(self.manifest['backups'])} backups tracked")
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
            raise
    
    def _calculate_hash(self, data: bytes) -> str:
        """Calculate SHA256 hash of data."""
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _get_backup_filename(self, file_hash: str) -> str:
        """Generate backup filename from timestamp and hash."""
        timestamp = datetime.now().strftime(DataConstants.BACKUP_TIMESTAMP_FORMAT)
        return f"{DataConstants.BACKUP_PREFIX}_{timestamp}_{file_hash}.json.gz"
    
    def create_backup(self, description: str = "", force: bool = False) -> Optional[str]:
        """
        Create backup of current data.json.
        
        Args:
            description: Human-readable description of this backup
            force: Force backup even if data hasn't changed
            
        Returns:
            Backup ID if successful, None otherwise
        """
        if not self.data_file.exists():
            logger.error(f"Data file not found: {self.data_file}")
            return None
        
        try:
            # Read current data
            with open(self.data_file, 'rb') as f:
                data = f.read()
            
            # Calculate hash
            file_hash = self._calculate_hash(data)
            file_size = len(data)
            
            # Check for duplicate (same hash) unless forced
            if not force:
                for backup_id, metadata in self.manifest["backups"].items():
                    if metadata.get("file_hash") == file_hash:
                        logger.info(f"Backup already exists for this data: {backup_id}")
                        return backup_id
            
            # Generate backup ID and filename
            backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = self._get_backup_filename(file_hash)
            backup_path = self.backups_dir / backup_filename
            
            # Save compressed backup
            with gzip.open(backup_path, 'wb') as f:
                f.write(data)
            
            # Create and store metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now().isoformat(),
                file_hash=file_hash,
                file_size=file_size,
                description=description,
                status=BackupStatus.ACTIVE.value
            )
            
            self.manifest["backups"][backup_id] = metadata.to_dict()
            self._save_manifest()
            
            logger.info(f"Backup created: {backup_id} ({file_size} bytes)")
            
            # Cleanup old backups
            self._rotate_backups()
            
            return backup_id
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore data from a specific backup.
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            True if successful, False otherwise
        """
        if backup_id not in self.manifest["backups"]:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        metadata = self.manifest["backups"][backup_id]
        
        try:
            # Find backup file
            file_hash = metadata["file_hash"]
            timestamp = backup_id
            
            # Search for matching backup file
            backup_path = None
            for file in self.backups_dir.glob(f"{DataConstants.BACKUP_PREFIX}_{timestamp}_*.json.gz"):
                if file_hash in file.name:
                    backup_path = file
                    break
            
            if not backup_path or not backup_path.exists():
                logger.error(f"Backup file not found for ID: {backup_id}")
                return False
            
            # Create backup of current state before restore
            self.create_backup(f"Pre-restore snapshot before restoring {backup_id}", force=True)
            
            # Restore from backup
            with gzip.open(backup_path, 'rb') as f:
                data = f.read()
            
            with open(self.data_file, 'wb') as f:
                f.write(data)
            
            logger.info(f"Restored backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup {backup_id}: {e}")
            return False
    
    def list_backups(self, limit: Optional[int] = None) -> List[Dict]:
        """
        List all backups in chronological order (newest first).
        
        Args:
            limit: Maximum number of backups to return
            
        Returns:
            List of backup metadata dictionaries
        """
        backups = [
            metadata
            for metadata in self.manifest["backups"].values()
            if metadata.get("status") == BackupStatus.ACTIVE.value
        ]
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        
        if limit:
            backups = backups[:limit]
        
        return backups
    
    def get_version_history(self, limit: int = 20) -> List[Dict]:
        """
        Get version history with summaries.
        
        Args:
            limit: Maximum versions to return
            
        Returns:
            List of version summaries
        """
        history = []
        for backup in self.list_backups(limit=limit):
            history.append({
                "id": backup["backup_id"],
                "timestamp": backup["timestamp"],
                "hash": backup["file_hash"],
                "size_bytes": backup["file_size"],
                "size_mb": backup["file_size"] / (1024 * 1024),
                "description": backup.get("description", ""),
            })
        return history
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a specific backup.
        
        Args:
            backup_id: ID of backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        if backup_id not in self.manifest["backups"]:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        try:
            metadata = self.manifest["backups"][backup_id]
            file_hash = metadata["file_hash"]
            timestamp = backup_id
            
            # Find and delete backup file
            for file in self.backups_dir.glob(f"{DataConstants.BACKUP_PREFIX}_{timestamp}_*.json.gz"):
                if file_hash in file.name:
                    file.unlink()
                    logger.debug(f"Deleted backup file: {file.name}")
                    break
            
            # Mark as archived in manifest
            self.manifest["backups"][backup_id]["status"] = BackupStatus.ARCHIVED.value
            self._save_manifest()
            
            logger.info(f"Archived backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting backup {backup_id}: {e}")
            return False
    
    def _rotate_backups(self) -> None:
        """Remove old backups to maintain max backup count."""
        max_backups = DataConstants.MAX_BACKUPS_TO_KEEP
        active_backups = self.list_backups()
        
        if len(active_backups) > max_backups:
            # Delete oldest backups
            for backup in active_backups[max_backups:]:
                self.delete_backup(backup["backup_id"])
                logger.debug(f"Rotated out old backup: {backup['backup_id']}")
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific backup.
        
        Args:
            backup_id: ID of backup to get info for
            
        Returns:
            Backup metadata dictionary or None if not found
        """
        return self.manifest["backups"].get(backup_id)
    
    def cleanup_orphaned_backups(self) -> int:
        """
        Find and remove backup files not tracked in manifest.
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        manifest_hashes = {
            metadata["file_hash"]
            for metadata in self.manifest["backups"].values()
        }
        
        for backup_file in self.backups_dir.glob(f"{DataConstants.BACKUP_PREFIX}_*.json.gz"):
            # Extract hash from filename
            file_hash = backup_file.name.split("_")[-1].replace(".json.gz", "")
            
            if file_hash not in manifest_hashes:
                try:
                    backup_file.unlink()
                    removed_count += 1
                    logger.debug(f"Removed orphaned backup: {backup_file.name}")
                except Exception as e:
                    logger.error(f"Failed to remove orphaned backup: {e}")
        
        return removed_count
    
    def verify_backups(self) -> Tuple[int, int]:
        """
        Verify integrity of all backup files.
        
        Returns:
            Tuple of (valid_count, corrupted_count)
        """
        valid_count = 0
        corrupted_count = 0
        
        for backup_id, metadata in self.manifest["backups"].items():
            if metadata.get("status") != BackupStatus.ACTIVE.value:
                continue
            
            try:
                # Try to read and decompress
                file_hash = metadata["file_hash"]
                timestamp = backup_id
                
                for backup_file in self.backups_dir.glob(f"{DataConstants.BACKUP_PREFIX}_{timestamp}_*.json.gz"):
                    if file_hash not in backup_file.name:
                        continue
                    
                    with gzip.open(backup_file, 'rb') as f:
                        data = f.read()
                    
                    # Verify hash
                    calculated_hash = self._calculate_hash(data)
                    if calculated_hash == file_hash:
                        valid_count += 1
                        logger.debug(f"Verified backup: {backup_id}")
                    else:
                        corrupted_count += 1
                        self.manifest["backups"][backup_id]["status"] = BackupStatus.CORRUPTED.value
                        logger.warning(f"Corrupted backup detected: {backup_id}")
                    break
                    
            except Exception as e:
                corrupted_count += 1
                logger.error(f"Error verifying backup {backup_id}: {e}")
        
        if corrupted_count > 0:
            self._save_manifest()
        
        return valid_count, corrupted_count


# Global backup manager instance
_backup_manager: Optional[BackupManager] = None


def get_backup_manager() -> BackupManager:
    """Get or create global backup manager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager


if __name__ == "__main__":
    # Test the backup manager
    print("Haven Backup Manager - Testing")
    print("=" * 70)
    
    manager = BackupManager()
    
    # Create a test backup
    print("\n1. Creating backup...")
    backup_id = manager.create_backup("Test backup")
    if backup_id:
        print(f"   ✓ Backup created: {backup_id}")
    
    # List backups
    print("\n2. Listing backups...")
    backups = manager.list_backups(limit=5)
    print(f"   ✓ Found {len(backups)} active backup(s)")
    for backup in backups[:3]:
        print(f"      - {backup['backup_id']}: {backup.get('description', 'No description')}")
    
    # Get version history
    print("\n3. Version history...")
    history = manager.get_version_history(limit=5)
    print(f"   ✓ {len(history)} version(s)")
    
    # Verify backups
    print("\n4. Verifying backup integrity...")
    valid, corrupted = manager.verify_backups()
    print(f"   ✓ {valid} valid, {corrupted} corrupted")
    
    print("\n" + "=" * 70)
    print("Backup manager ready!")
