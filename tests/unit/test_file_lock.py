"""
Test File Locking Functionality

Tests the FileLock class to ensure it properly prevents concurrent access
to files and handles various edge cases.
"""

import sys
from pathlib import Path
import time
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.file_lock import FileLock


def test_basic_locking():
    """Test that basic file locking works."""
    print("\n[TEST] Basic File Locking")
    print("=" * 70)

    test_file = Path(__file__).parent / "test_lock_file.txt"
    test_file.write_text("initial content")

    try:
        # Acquire lock
        with FileLock(test_file, timeout=5.0):
            print(f"  [OK] Lock acquired on {test_file.name}")

            # Write to file while holding lock
            test_file.write_text("locked content")
            print(f"  [OK] File written while holding lock")

            # Check that lock file exists
            lock_file = test_file.with_suffix(test_file.suffix + '.lock')
            if lock_file.exists():
                print(f"  [OK] Lock file created: {lock_file.name}")
            else:
                print(f"  [FAIL] Lock file not found")
                return False

        # Check that lock file was cleaned up
        if not lock_file.exists():
            print(f"  [OK] Lock file cleaned up after release")
        else:
            print(f"  [FAIL] Lock file still exists after release")
            lock_file.unlink(missing_ok=True)
            return False

        print(f"  [OK] Content verified: {test_file.read_text()}")
        return True

    finally:
        # Clean up
        test_file.unlink(missing_ok=True)


def test_concurrent_access():
    """Test that concurrent access is blocked."""
    print("\n[TEST] Concurrent Access Prevention")
    print("=" * 70)

    test_file = Path(__file__).parent / "test_concurrent.txt"
    test_file.write_text("initial")

    results = {"thread1_acquired": False, "thread2_blocked": False, "thread2_acquired_after": False}

    def thread1_func():
        """Hold lock for 2 seconds."""
        with FileLock(test_file, timeout=5.0):
            results["thread1_acquired"] = True
            print(f"  [OK] Thread 1: Lock acquired")
            time.sleep(2)  # Hold lock for 2 seconds
            print(f"  [OK] Thread 1: Releasing lock")

    def thread2_func():
        """Try to acquire lock (should be blocked)."""
        time.sleep(0.5)  # Wait for thread1 to acquire lock
        print(f"  [OK] Thread 2: Attempting to acquire lock...")

        start_time = time.time()
        try:
            with FileLock(test_file, timeout=5.0):
                elapsed = time.time() - start_time
                if elapsed > 1.0:  # Should have waited for thread1
                    results["thread2_blocked"] = True
                    print(f"  [OK] Thread 2: Lock acquired after {elapsed:.2f}s (was blocked)")
                    results["thread2_acquired_after"] = True
                else:
                    print(f"  [FAIL] Thread 2: Lock acquired too quickly ({elapsed:.2f}s)")
        except TimeoutError:
            print(f"  [FAIL] Thread 2: Timed out")

    try:
        # Start both threads
        t1 = threading.Thread(target=thread1_func)
        t2 = threading.Thread(target=thread2_func)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Verify results
        success = all([
            results["thread1_acquired"],
            results["thread2_blocked"],
            results["thread2_acquired_after"]
        ])

        if success:
            print(f"  [OK] Concurrent access properly blocked")
        else:
            print(f"  [FAIL] Concurrent access test failed: {results}")

        return success

    finally:
        # Clean up
        test_file.unlink(missing_ok=True)
        lock_file = test_file.with_suffix('.txt.lock')
        lock_file.unlink(missing_ok=True)


def test_timeout():
    """Test that lock timeout works."""
    print("\n[TEST] Lock Timeout")
    print("=" * 70)

    test_file = Path(__file__).parent / "test_timeout.txt"
    test_file.write_text("initial")

    try:
        # Acquire lock and hold it
        lock1 = FileLock(test_file, timeout=2.0)
        lock1.__enter__()
        print(f"  [OK] Lock 1 acquired")

        # Try to acquire again with short timeout (should fail)
        try:
            with FileLock(test_file, timeout=1.0):
                print(f"  [FAIL] Lock 2 should have timed out")
                return False
        except TimeoutError as e:
            print(f"  [OK] Lock 2 timed out as expected: {str(e)[:50]}...")

        # Release first lock
        lock1.__exit__(None, None, None)
        print(f"  [OK] Lock 1 released")

        # Now lock 3 should succeed
        with FileLock(test_file, timeout=2.0):
            print(f"  [OK] Lock 3 acquired after lock 1 released")

        return True

    finally:
        # Clean up
        test_file.unlink(missing_ok=True)
        lock_file = test_file.with_suffix('.txt.lock')
        lock_file.unlink(missing_ok=True)


def test_stale_lock_detection():
    """Test that stale locks are detected and removed."""
    print("\n[TEST] Stale Lock Detection")
    print("=" * 70)

    test_file = Path(__file__).parent / "test_stale.txt"
    test_file.write_text("initial")
    lock_file = test_file.with_suffix('.txt.lock')

    try:
        # Create a fake "stale" lock file
        lock_file.write_text("fake stale lock")
        print(f"  [OK] Created fake lock file")

        # Modify the timestamp to make it old (>5 minutes)
        import os
        old_time = time.time() - (6 * 60)  # 6 minutes ago
        os.utime(lock_file, (old_time, old_time))
        print(f"  [OK] Set lock file timestamp to 6 minutes ago")

        # Try to acquire lock - should detect stale lock and succeed
        with FileLock(test_file, timeout=2.0):
            print(f"  [OK] Stale lock detected and removed, new lock acquired")

        return True

    finally:
        # Clean up
        test_file.unlink(missing_ok=True)
        lock_file.unlink(missing_ok=True)


def run_all_tests():
    """Run all file locking tests."""
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "=" * 70)
    print("[FILE LOCK] File Locking Tests")
    print("=" * 70)

    tests = [
        ("Basic Locking", test_basic_locking),
        ("Concurrent Access Prevention", test_concurrent_access),
        ("Lock Timeout", test_timeout),
        ("Stale Lock Detection", test_stale_lock_detection),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n  [FAIL] Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("[SUMMARY] Test Results")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    print("\n" + "=" * 70)
    print(f"  Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("  [SUCCESS] ALL FILE LOCKING TESTS PASSED!")
    else:
        print(f"  [WARN] {total_count - passed_count} test(s) failed")

    print("=" * 70 + "\n")

    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)


# ============================================================================
# PYTEST-BASED UNIT TESTS WITH MOCKING
# ============================================================================

import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os


class TestFileLockContext:
    """Test FileLock context manager functionality."""

    @pytest.mark.unit
    def test_lock_acquisition(self, tmp_path):
        """Test that lock can be acquired and released."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        lock = FileLock(test_file, timeout=5.0)
        assert not lock._acquired
        
        with lock:
            assert lock._acquired
            assert lock.fp is not None
        
        assert not lock._acquired
        assert lock.fp is None

    @pytest.mark.unit
    def test_lock_file_created(self, tmp_path):
        """Test that lock file is created during locking."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        lock = FileLock(test_file)
        lock_file = lock.lock_file
        
        assert not lock_file.exists()
        
        with lock:
            assert lock_file.exists()
        
        assert not lock_file.exists()

    @pytest.mark.unit
    def test_lock_timeout(self, tmp_path):
        """Test that lock times out if not available."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Create first lock
        lock1 = FileLock(test_file, timeout=0.5)
        
        with lock1:
            # Try to acquire second lock while first is held
            lock2 = FileLock(test_file, timeout=0.5)
            
            with pytest.raises(TimeoutError):
                with lock2:
                    pass

    @pytest.mark.unit
    def test_is_locked_check(self, tmp_path):
        """Test checking if file is currently locked."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        lock = FileLock(test_file)
        
        assert not lock.is_locked()
        
        with lock:
            assert lock.is_locked()
        
        assert not lock.is_locked()


class TestFileLockStaleHandling:
    """Test handling of stale lock files."""

    @pytest.mark.unit
    def test_stale_lock_detection(self, tmp_path):
        """Test detection of stale lock files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        lock = FileLock(test_file)
        
        # Manually create an old lock file
        lock_file = lock.lock_file
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text("stale lock")
        
        # Make it appear old (more than 5 minutes)
        old_time = time.time() - 400
        os.utime(str(lock_file), (old_time, old_time))
        
        # Should detect as stale
        assert lock._is_stale_lock()

    @pytest.mark.unit
    def test_recent_lock_not_stale(self, tmp_path):
        """Test that recent locks are not considered stale."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        lock = FileLock(test_file)
        lock_file = lock.lock_file
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text("recent lock")
        
        # Should not be stale (just created)
        assert not lock._is_stale_lock()


class TestFileLockConcurrency:
    """Test FileLock with concurrent access."""

    @pytest.mark.unit
    def test_sequential_lock_access(self, tmp_path):
        """Test sequential lock access by multiple threads."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("0")
        
        results = []
        
        def increment_file():
            lock = FileLock(test_file, timeout=10)
            with lock:
                current = int(test_file.read_text())
                time.sleep(0.1)  # Simulate work
                test_file.write_text(str(current + 1))
                results.append(True)
        
        # Create threads
        threads = [threading.Thread(target=increment_file) for _ in range(3)]
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for all to complete
        for t in threads:
            t.join(timeout=30)
        
        # All threads should have completed
        assert len(results) == 3
        assert test_file.read_text() == "3"


class TestFileLockPathHandling:
    """Test FileLock path handling."""

    @pytest.mark.unit
    def test_lock_dir_creation(self, tmp_path):
        """Test that lock directory is created if needed."""
        test_file = tmp_path / "subdir" / "test.txt"
        test_file.parent.mkdir()
        test_file.write_text("content")
        
        lock = FileLock(test_file)
        
        # Lock directory should be created
        assert lock.lock_dir.exists()

    @pytest.mark.unit
    def test_custom_lock_dir(self, tmp_path):
        """Test using custom lock directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        custom_lock_dir = tmp_path / "custom_locks"
        lock = FileLock(test_file, lock_dir=str(custom_lock_dir))
        
        assert lock.lock_dir == custom_lock_dir

