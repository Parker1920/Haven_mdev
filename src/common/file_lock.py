"""
File Locking for Concurrent Access

Provides cross-platform file locking to prevent data corruption when
multiple processes try to access the same file simultaneously.

Usage:
    from common.file_lock import FileLock

    with FileLock(data_file):
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
"""

import sys
import time
from pathlib import Path
from typing import Optional, IO, Any


class FileLock:
    """Cross-platform file locking context manager.

    Provides exclusive access to a file by creating a .lock file.
    Works on Windows, macOS, and Linux.

    Attributes:
        path: Path to the file to lock
        lock_file: Path to the .lock file
        timeout: Maximum seconds to wait for lock (default: 30)
        check_interval: Seconds between lock attempts (default: 0.1)

    Example:
        >>> data_file = Path('data/data.json')
        >>> with FileLock(data_file, timeout=10):
        ...     with open(data_file, 'w') as f:
        ...         json.dump(data, f, indent=2)
    """

    def __init__(self, path: Path, timeout: float = 30.0, check_interval: float = 0.1):
        """Initialize file lock.

        Args:
            path: Path to file that needs locking
            timeout: Maximum seconds to wait for lock (default: 30)
            check_interval: Seconds between lock attempts (default: 0.1)
        """
        self.path = Path(path)
        self.lock_file = self.path.with_suffix(self.path.suffix + '.lock')
        self.timeout = timeout
        self.check_interval = check_interval
        self.fp: Optional[IO[Any]] = None
        self._acquired = False

    def __enter__(self):
        """Acquire the lock.

        Returns:
            self

        Raises:
            TimeoutError: If lock cannot be acquired within timeout period
        """
        start_time = time.time()

        while True:
            try:
                # Try to create lock file exclusively
                # 'x' mode fails if file already exists
                self.fp = open(self.lock_file, 'x')
                self.fp.write(f"Locked by PID {sys.platform} at {time.time()}\n")
                self.fp.flush()
                self._acquired = True
                return self

            except FileExistsError:
                # Lock file exists, check if it's stale
                if self._is_stale_lock():
                    # Remove stale lock and try again
                    try:
                        self.lock_file.unlink()
                    except FileNotFoundError:
                        pass  # Someone else removed it
                    continue

                # Check timeout
                elapsed = time.time() - start_time
                if elapsed >= self.timeout:
                    raise TimeoutError(
                        f"Could not acquire lock on {self.path} after {self.timeout}s. "
                        f"Another process may be using this file."
                    )

                # Wait and try again
                time.sleep(self.check_interval)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the lock.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        if self._acquired:
            try:
                if self.fp:
                    self.fp.close()
                    self.fp = None

                # Remove lock file
                if self.lock_file.exists():
                    self.lock_file.unlink()

            except Exception as e:
                # Log but don't raise - we're cleaning up
                import logging
                logging.warning(f"Error releasing lock on {self.path}: {e}")

            finally:
                self._acquired = False

    def _is_stale_lock(self) -> bool:
        """Check if lock file is stale (abandoned by crashed process).

        A lock is considered stale if it's older than 5 minutes.
        This is a safety mechanism to recover from crashes.

        Returns:
            True if lock appears stale, False otherwise
        """
        try:
            if not self.lock_file.exists():
                return False

            # Check lock file age
            lock_age = time.time() - self.lock_file.stat().st_mtime

            # If lock is older than 5 minutes, consider it stale
            if lock_age > 300:  # 5 minutes
                return True

            return False

        except Exception:
            # If we can't check, assume not stale
            return False

    def is_locked(self) -> bool:
        """Check if file is currently locked (without acquiring lock).

        Returns:
            True if lock file exists, False otherwise
        """
        return self.lock_file.exists() and not self._is_stale_lock()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def with_file_lock(path: Path, timeout: float = 30.0):
    """Decorator to add file locking to a function.

    Args:
        path: Path to file to lock
        timeout: Maximum seconds to wait for lock

    Example:
        >>> @with_file_lock(Path('data/data.json'))
        ... def save_data(data):
        ...     with open('data/data.json', 'w') as f:
        ...         json.dump(data, f)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with FileLock(path, timeout=timeout):
                return func(*args, **kwargs)
        return wrapper
    return decorator
