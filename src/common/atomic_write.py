"""
Atomic File Writing Utilities

Provides safe file writing with rollback protection.
Prevents data corruption from partial writes or crashes during save operations.

Usage:
    from common.atomic_write import atomic_write_json

    data = {"systems": [...]}
    atomic_write_json(data, "data/data.json")
"""
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def atomic_write_json(data: Dict[str, Any], target_path: str | Path, indent: int = 2):
    """
    Atomically write JSON data to a file with rollback protection.

    This function:
    1. Writes data to a temporary file
    2. Verifies the write succeeded
    3. Creates a backup of the original file (if it exists)
    4. Atomically replaces the original with the temp file
    5. Cleans up backup on success

    If any step fails, the original file remains unchanged.

    Args:
        data: Dictionary to write as JSON
        target_path: Path to target file
        indent: JSON indentation (default: 2)

    Raises:
        Exception: If write fails (original file remains intact)

    Example:
        try:
            atomic_write_json(systems_data, "data/data.json")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    """
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in same directory as target
    # (ensures same filesystem for atomic rename)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=target_path.parent,
        prefix=f".{target_path.name}.",
        suffix=".tmp"
    )

    temp_path = Path(temp_path)
    backup_path = None

    try:
        # Write to temporary file
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk

        logger.debug(f"Wrote data to temporary file: {temp_path}")

        # Verify temp file is valid JSON
        with open(temp_path, 'r', encoding='utf-8') as f:
            json.load(f)  # Will raise JSONDecodeError if invalid

        logger.debug("Verified temporary file is valid JSON")

        # If target exists, create backup
        if target_path.exists():
            backup_path = target_path.with_suffix(target_path.suffix + '.backup')
            shutil.copy2(target_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")

        # Atomic replace (rename is atomic on POSIX and Windows)
        # On Windows, need to remove target first if it exists
        if os.name == 'nt' and target_path.exists():
            target_path.unlink()

        temp_path.rename(target_path)
        logger.info(f"Atomically wrote JSON to: {target_path}")

        # Clean up backup on success
        if backup_path and backup_path.exists():
            backup_path.unlink()
            logger.debug("Removed backup file")

    except Exception as e:
        # Rollback: restore from backup if it exists
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, target_path)
            backup_path.unlink()
            logger.warning(f"Restored from backup due to error: {e}")

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        logger.error(f"Atomic write failed for {target_path}: {e}")
        raise


def atomic_write_text(text: str, target_path: str | Path, encoding: str = 'utf-8'):
    """
    Atomically write text to a file with rollback protection.

    Similar to atomic_write_json but for plain text files.

    Args:
        text: Text content to write
        target_path: Path to target file
        encoding: Text encoding (default: utf-8)

    Raises:
        Exception: If write fails (original file remains intact)
    """
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in same directory as target
    temp_fd, temp_path = tempfile.mkstemp(
        dir=target_path.parent,
        prefix=f".{target_path.name}.",
        suffix=".tmp"
    )

    temp_path = Path(temp_path)
    backup_path = None

    try:
        # Write to temporary file
        with os.fdopen(temp_fd, 'w', encoding=encoding) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())

        logger.debug(f"Wrote text to temporary file: {temp_path}")

        # If target exists, create backup
        if target_path.exists():
            backup_path = target_path.with_suffix(target_path.suffix + '.backup')
            shutil.copy2(target_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")

        # Atomic replace
        if os.name == 'nt' and target_path.exists():
            target_path.unlink()

        temp_path.rename(target_path)
        logger.info(f"Atomically wrote text to: {target_path}")

        # Clean up backup on success
        if backup_path and backup_path.exists():
            backup_path.unlink()

    except Exception as e:
        # Rollback
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, target_path)
            backup_path.unlink()
            logger.warning(f"Restored from backup due to error: {e}")

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        logger.error(f"Atomic write failed for {target_path}: {e}")
        raise
