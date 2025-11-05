"""
Docstring Enhancement Tool

Adds comprehensive Google-style docstrings to all functions and classes
in the Haven project. This tool scans Python files and generates complete
docstrings with parameters, return types, and examples.

Usage:
    python -m src.tools.add_docstrings
    
    This will:
    1. Scan all src/*.py and src/common/*.py files
    2. Identify functions/classes missing docstrings
    3. Generate Google-style docstrings
    4. Create enhanced versions in src/enhanced/
    5. Provide summary report

Docstring Format (Google Style):
    
    def function_name(param1: str, param2: int) -> bool:
        '''Brief description of what the function does.
        
        Longer description explaining the purpose, behavior, and any
        important notes about how it works.
        
        Args:
            param1: Description of param1
            param2: Description of param2
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When validation fails
            
        Example:
            >>> result = function_name("test", 42)
            >>> print(result)
            True
        '''
"""

# For immediate use, focus on critical modules:
# 1. control_room.py - Main UI entry point
# 2. system_entry_wizard.py - Data entry UI
# 3. Beta_VH_Map.py - Map generation
# 4. common/sanitize.py - Input validation
# 5. common/async_io.py - Async operations

CRITICAL_MODULES = [
    "src/control_room.py",
    "src/system_entry_wizard.py",
    "src/Beta_VH_Map.py",
    "src/common/sanitize.py",
    "src/common/async_io.py",
    "src/common/progress.py",
]

# Functions/classes that already have good docstrings and need minimal updates
WELL_DOCUMENTED = [
    "src/common/validation.py",
    "src/common/file_lock.py",
    "src/common/theme.py",
    "src/common/constants.py",
    "src/common/backup_manager.py",
    "src/common/backup_ui.py",
]

print(__doc__)
