# Test Manager Guide

## Overview

The **Test Manager** is a comprehensive GUI tool for managing, running, and tracking all test scripts in the Haven Control Room project. It provides a centralized interface for test execution with real-time output, result tracking, and test organization.

## Location

**Access:** Control Room → Advanced Tools → 🧪 Test Manager

## Features

### 1. Test Organization
- **Hierarchical Structure:** Tests organized into 7 main categories:
  - **Control-Room:** Control Room UI, database, and integration tests
  - **Wizard:** System Entry Wizard tests
  - **Keeper:** Discord bot tests
  - **Map-Generation:** 3D map generation tests
  - **User-Edition:** User Edition feature tests
  - **Utilities:** Utility script tests
  - **Security:** Security and validation tests

- **Subcategories:** Each main category has logical subcategories (e.g., Control-Room/Database, Control-Room/UI)

### 2. Test Execution
- **Run Individual Tests:** Select and run any test file
- **Real-time Output:** View stdout and stderr as tests execute
- **Progress Indicator:** Animated progress bar shows test is running
- **Timeout Protection:** 5-minute timeout prevents hanging tests
- **Return Code Display:** See exit codes for debugging

### 3. Test Information
Each test displays:
- **Name:** Test file name
- **Description:** Extracted from file docstring
- **Modified Date:** Last modification timestamp
- **Last Run Status:** ✅ Pass or ❌ Fail
- **Runtime:** Execution time in seconds

### 4. Test Management
- **Edit Test:** Opens test in default Python editor
- **Add New Test:** Import test files via file browser
  - Prompts for category and subcategory
  - Automatically organizes into Program-tests structure
- **View Results History:** See all past runs for a test

### 5. Results Tracking
- **Persistent Database:** test_results.json stores all test history
- **Export Results:** Export full test results to JSON file
- **Status Tracking:** Keeps track of pass/fail status and timing

## Usage

### Running a Test

1. Launch Control Room
2. Click **🧪 Test Manager** in Advanced Tools
3. Browse the test categories in the left panel
4. Click on any test to select it
5. Review test info in the right panel
6. Click **Run Test** button
7. Watch progress bar and output in real-time
8. Results are automatically saved to history

### Adding a New Test

1. Click **Add New Test** button
2. Browse to your Python test file
3. Select the main category (e.g., "Control-Room")
4. Enter subcategory (e.g., "Database")
5. Test is copied to Program-tests/[Category]/[Subcategory]/

### Editing a Test

1. Select the test in the tree view
2. Click **Edit Test** button
3. Test opens in your default Python editor
4. Make changes and save
5. Changes take effect immediately

### Exporting Results

1. Click **Export Results** button
2. Choose export location
3. JSON file contains:
   - All test results
   - Timestamps
   - Pass/fail status
   - Runtime data
   - Export metadata

## File Structure

```
Program-tests/
├── TEST_MANIFEST.md          # Documentation
├── test_results.json          # Results database
├── Control-Room/
│   ├── Database/
│   ├── UI/
│   ├── Integration/
│   └── Performance/
├── Wizard/
│   ├── Data-Entry/
│   ├── Validation/
│   └── Save-Load/
├── Keeper/
│   ├── Commands/
│   ├── Database/
│   └── Discord-Integration/
├── Map-Generation/
├── User-Edition/
├── Utilities/
└── Security/
```

## Test Results Database

**Location:** `Program-tests/test_results.json`

**Format:**
```json
{
  "test_name.py": {
    "status": "passed",
    "runtime": 2.45,
    "timestamp": "2025-11-13T20:15:30",
    "returncode": 0
  }
}
```

## Writing Tests for Test Manager

### Test File Requirements

1. **Valid Python File:** Must be a .py file with valid syntax
2. **Docstring (Recommended):** First docstring becomes test description
3. **Standalone Execution:** Should run independently
4. **Exit Code:** Return 0 for success, non-zero for failure

### Example Test Structure

```python
"""
Test Description Goes Here

This will be displayed in the Test Manager info panel.
"""

import sys
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

def main():
    """Main test logic"""
    try:
        # Test code here
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## Best Practices

### Test Organization
- Use clear, descriptive file names: `test_feature_name.py`
- Place tests in appropriate categories
- Use subcategories for logical grouping
- Keep test files focused on single functionality

### Test Output
- Use clear success/failure indicators (✓/✗)
- Print helpful diagnostic information
- Include test steps in output
- Use proper exit codes (0 = success, 1+ = failure)

### Test Reliability
- Make tests idempotent (can run multiple times)
- Don't depend on external state
- Clean up resources after test
- Handle expected exceptions gracefully
- Use timeouts for long-running operations

### Documentation
- Always include a docstring describing the test
- Explain what the test validates
- Document any special requirements or setup

## Troubleshooting

### Test Won't Run
- Check Python syntax (use `python3 -m py_compile test_file.py`)
- Verify imports are correct
- Ensure test has execution permissions
- Check timeout (5 minutes max)

### Test Results Not Saving
- Verify Program-tests/ directory exists
- Check write permissions on test_results.json
- Review Test Manager logs in Control Room output

### Can't Add Test
- Ensure file has .py extension
- Check file isn't already in Program-tests/
- Verify you have write permissions

### Output Not Displaying
- Check that test prints to stdout/stderr
- Verify test isn't buffering output
- Use `flush=True` in print statements if needed

## Integration with Control Room

The Test Manager is fully integrated into the Control Room's Advanced Tools section:

- **Same Theme:** Uses Control Room's glassmorphic theme
- **Consistent Colors:** Matches Control Room color scheme
- **Parent Window:** Opens as child of Control Room
- **Logging:** Logs actions to Control Room's status panel

## Technical Details

### Implementation
- **File:** `src/test_manager_window.py`
- **Class:** `TestManagerWindow(ctk.CTkToplevel)`
- **GUI Framework:** CustomTkinter
- **Test Discovery:** Auto-discovers all .py files in Program-tests/
- **Execution:** Subprocess with timeout and output capture
- **Threading:** Background execution prevents UI freezing

### Dependencies
- customtkinter
- tkinter
- subprocess
- threading
- json

## Future Enhancements

Potential future features:
- Run multiple tests in sequence
- Filter tests by status or category
- Search tests by name or description
- Compare test results over time
- Generate test reports (HTML/PDF)
- Test scheduling/automation
- Coverage analysis integration

## See Also

- [TEST_MANIFEST.md](../../Program-tests/TEST_MANIFEST.md) - Complete list of organized tests
- [Control Room Guide](CONTROL_ROOM_GUIDE.md) - Control Room documentation
- [System Test Guide](SYSTEM_TEST_GUIDE.md) - System test suite documentation

---

**Last Updated:** November 13, 2025
**Version:** 1.0
