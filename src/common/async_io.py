"""
Async File Operations Module

Provides asynchronous file I/O operations for better performance during
data loading, saving, and processing operations.

Features:
- Async JSON reading/writing
- Async file copy operations
- Thread pool execution for blocking I/O
- Progress callbacks during operations

Usage:
    from common.async_io import async_read_json, async_write_json
    import asyncio

    async def main():
        data = await async_read_json('data/data.json')
        data['newkey'] = 'value'
        await async_write_json(data, 'data/data.json')

    asyncio.run(main())
"""

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

# Thread pool for blocking I/O operations
_executor = ThreadPoolExecutor(max_workers=2)


async def async_read_json(
    file_path: Path | str,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Asynchronously read and parse a JSON file.

    Args:
        file_path: Path to JSON file
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    file_path = Path(file_path)
    
    def _read():
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(_executor, _read)
        logger.debug(f"Async read completed: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise


async def async_write_json(
    data: Dict[str, Any],
    file_path: Path | str,
    encoding: str = "utf-8",
    indent: int = 2,
    backup: bool = True
) -> None:
    """
    Asynchronously write data to a JSON file.

    Args:
        data: Data to write
        file_path: Path to output file
        encoding: File encoding (default: utf-8)
        indent: JSON indentation level (default: 2)
        backup: Create backup before overwriting (default: True)

    Raises:
        IOError: If write fails
    """
    file_path = Path(file_path)
    
    def _write():
        # Create backup if requested and file exists
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Backup created: {backup_path}")
        
        # Write JSON atomically using temp file
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        with open(temp_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        # Atomic rename
        temp_path.replace(file_path)
        logger.debug(f"Async write completed: {file_path}")
    
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(_executor, _write)
    except IOError as e:
        logger.error(f"Failed to write {file_path}: {e}")
        raise


async def async_copy_file(
    src: Path | str,
    dst: Path | str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> None:
    """
    Asynchronously copy a file with optional progress reporting.

    Args:
        src: Source file path
        dst: Destination file path
        progress_callback: Optional callback(bytes_copied, total_bytes)

    Raises:
        FileNotFoundError: If source doesn't exist
    """
    src = Path(src)
    dst = Path(dst)
    
    def _copy():
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")
        
        if progress_callback:
            total_size = src.stat().st_size
            
            def _copy_with_progress():
                with open(src, 'rb') as src_file:
                    with open(dst, 'wb') as dst_file:
                        bytes_copied = 0
                        while True:
                            chunk = src_file.read(1024 * 1024)  # 1MB chunks
                            if not chunk:
                                break
                            dst_file.write(chunk)
                            bytes_copied += len(chunk)
                            progress_callback(bytes_copied, total_size)
            
            _copy_with_progress()
        else:
            shutil.copy2(src, dst)
        
        logger.debug(f"Async copy completed: {src} -> {dst}")
    
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(_executor, _copy)
    except FileNotFoundError as e:
        logger.error(f"Copy failed: {e}")
        raise


async def async_load_multiple_json(
    file_paths: list[Path | str]
) -> Dict[str, Any]:
    """
    Asynchronously load multiple JSON files concurrently.

    Args:
        file_paths: List of paths to JSON files

    Returns:
        Dictionary with filenames as keys and parsed data as values

    Example:
        >>> files = ['data1.json', 'data2.json']
        >>> results = await async_load_multiple_json(files)
    """
    tasks = [async_read_json(f) for f in file_paths]
    data_list = await asyncio.gather(*tasks, return_exceptions=True)
    
    results = {}
    for file_path, data in zip(file_paths, data_list):
        if isinstance(data, Exception):
            logger.error(f"Error loading {file_path}: {data}")
            results[str(file_path)] = None
        else:
            results[str(file_path)] = data
    
    return results


async def async_batch_write_json(
    data_dict: Dict[str, Dict[str, Any]],
    output_dir: Path | str
) -> None:
    """
    Asynchronously write multiple JSON files from a dictionary.

    Args:
        data_dict: Dictionary with filenames as keys and data as values
        output_dir: Directory to write files to

    Example:
        >>> data = {
        ...     'systems.json': {'systems': [...]},
        ...     'metadata.json': {'version': '3.0.0'}
        ... }
        >>> await async_batch_write_json(data, 'output')
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tasks = [
        async_write_json(data, output_dir / filename)
        for filename, data in data_dict.items()
    ]
    
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.debug(f"Batch write completed: {len(data_dict)} files to {output_dir}")


def sync_read_json(
    file_path: Path | str,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Synchronous wrapper for async_read_json for backward compatibility.

    Args:
        file_path: Path to JSON file
        encoding: File encoding

    Returns:
        Parsed JSON data
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context, create new loop
            new_loop = asyncio.new_event_loop()
            result = new_loop.run_until_complete(async_read_json(file_path, encoding))
            new_loop.close()
            return result
        else:
            return loop.run_until_complete(async_read_json(file_path, encoding))
    except RuntimeError:
        # No event loop, create new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_read_json(file_path, encoding))
        loop.close()
        return result


def sync_write_json(
    data: Dict[str, Any],
    file_path: Path | str,
    encoding: str = "utf-8",
    indent: int = 2,
    backup: bool = True
) -> None:
    """
    Synchronous wrapper for async_write_json for backward compatibility.

    Args:
        data: Data to write
        file_path: Path to output file
        encoding: File encoding
        indent: JSON indentation
        backup: Create backup
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            new_loop = asyncio.new_event_loop()
            new_loop.run_until_complete(
                async_write_json(data, file_path, encoding, indent, backup)
            )
            new_loop.close()
        else:
            loop.run_until_complete(
                async_write_json(data, file_path, encoding, indent, backup)
            )
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            async_write_json(data, file_path, encoding, indent, backup)
        )
        loop.close()
