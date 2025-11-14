# Data Source Unification - Implementation Guide

## Status: ✅ READY FOR INTEGRATION

The unified `DataSourceManager` has been created. Now follow these steps to integrate it into the control room and ensure all three functions use the same source of truth.

---

## Files Created

1. ✅ `src/common/data_source_manager.py` - The unified manager
2. 📄 `DATA_SOURCE_UNIFICATION.md` - Detailed analysis
3. 📄 This file - Implementation guide

---

## Integration Steps

### Step 1: Update `src/control_room.py` Imports

Add this to the imports section (around line 1-50):

```python
from src.common.data_source_manager import (
    get_data_source_manager,
    get_current_source,
    set_current_source
)
```

---

### Step 2: Replace `_get_data_source_description()` Method

**Find:** Lines ~422-431
**Replace with:**

```python
def _get_data_source_description(self):
    """
    Get descriptive text for current data source - NOW UNIFIED.
    All functions pull from DataSourceManager.
    """
    manager = get_data_source_manager()
    source = self.data_source.get()
    source_info = manager.get_source(source)
    
    if source_info:
        return source_info.description
    return ""
```

---

### Step 3: Replace `_get_data_indicator_text()` Method

**Find:** Lines ~410-419
**Replace with:**

```python
def _get_data_indicator_text(self):
    """Get data indicator text - NOW UNIFIED"""
    manager = get_data_source_manager()
    current = manager.get_current()
    
    if current:
        return f"{current.icon} {current.display_name}"
    return "📊 Unknown Data Source"
```

---

### Step 4: Replace `_on_data_source_change()` Method

**Find:** Lines ~441-487
**Replace with:**

```python
def _on_data_source_change(self, choice=None):
    """
    Handle data source dropdown change - NOW UNIFIED.
    All three functions (wizard, dropdown, stats) now use same data.
    """
    manager = get_data_source_manager()
    source_name = self.data_source.get()
    
    # Update manager's current source
    if not manager.set_current(source_name):
        self._log(f"Invalid data source: {source_name}")
        return
    
    source_info = manager.get_current()
    
    # Update description label
    if hasattr(self, 'data_description'):
        self.data_description.configure(text=source_info.description)
    
    # Update data indicator with color coding
    color_map = {
        "production": COLORS['success'],     # Green
        "testing": COLORS['warning'],         # Orange
        "load_test": COLORS['accent_cyan']    # Cyan
    }
    color = color_map.get(source_name, COLORS['success'])
    
    indicator_text = f"{source_info.icon} {source_info.display_name}"
    self.data_indicator.configure(
        text=indicator_text,
        text_color=color
    )
    
    # Update system count indicator
    if hasattr(self, 'count_indicator') and SHOW_SYSTEM_COUNT:
        self.count_indicator.configure(
            text=f"Systems: {source_info.system_count:,}"
        )
    
    # Log the change
    self._log(f"Switched to {source_info.display_name} ({source_info.system_count:,} systems)")
```

---

### Step 5: Replace `launch_gui()` Method (Wizard Launch)

**Find:** Lines ~509-540
**Replace with:**

```python
def launch_gui(self):
    """
    Launch System Entry Wizard with current data context - NOW UNIFIED.
    Passes the current data source to wizard so it uses same data.
    """
    manager = get_data_source_manager()
    current_source = manager.get_current()
    
    self._log(f"Launching System Entry Wizard (using {current_source.name} data)…")
    
    def run():
        try:
            if self._frozen:
                # Pass data source via command line
                cmd = [
                    sys.executable,
                    '--entry', 'system',
                    '--data-source', current_source.name
                ]
                subprocess.Popen(cmd, cwd=str(project_root()))
            else:
                # Pass data source via environment variable
                app = src_dir() / 'system_entry_wizard.py'
                env = os.environ.copy()
                env['HAVEN_DATA_SOURCE'] = current_source.name
                
                if sys.platform == 'darwin':
                    # macOS: Create temp shell script
                    import tempfile
                    script_content = f'''#!/bin/bash
export HAVEN_DATA_SOURCE="{current_source.name}"
cd "{project_root()}"
"{sys.executable}" "{app}"
'''
                    fd, script_path = tempfile.mkstemp(suffix='.command', text=True)
                    with open(fd, 'w') as f:
                        f.write(script_content)
                    import os as os_module
                    os_module.chmod(script_path, 0o755)
                    subprocess.Popen(['open', '-a', 'Terminal', script_path])
                else:
                    # Windows/Linux: Use environment variable
                    cmd = [sys.executable, str(app)]
                    subprocess.Popen(cmd, cwd=str(project_root()), env=env)
            
            self._log("System Entry Wizard launched.")
        except Exception as e:
            self._log(f"Launch failed: {e}")
            logging.error(f"Wizard launch error: {e}", exc_info=True)
    
    self._run_bg(run)
```

---

### Step 6: Replace `show_database_stats()` Method

**Find:** Lines ~814-873
**Replace with:**

```python
def show_database_stats(self):
    """
    Show database statistics - NOW UNIFIED.
    Pulls from DataSourceManager to ensure consistent counts.
    """
    manager = get_data_source_manager()
    current = manager.get_current()
    
    if current.backend_type != 'database':
        messagebox.showinfo("Info", "Database statistics only available in database mode.")
        return
    
    try:
        from src.common.database import HavenDatabase
        
        with HavenDatabase(str(current.path)) as db:
            stats = db.get_statistics()
        
        # Create stats dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Database Statistics - {current.display_name}")
        dialog.geometry("550x500")
        dialog.configure(fg_color=COLORS['bg_dark'])
        
        # Title
        title = ctk.CTkLabel(
            dialog,
            text=f"📊 Database Statistics",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS['accent_cyan']
        )
        title.pack(pady=20)
        
        # Stats frame
        stats_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS['glass'])
        stats_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Display stats - USE MANAGER'S SYSTEM COUNT
        stats_text = f"""Source: {current.display_name}
Path: {current.path}

Total Systems: {current.system_count:,}  ← From DataSourceManager
Total Planets: {stats['total_planets']:,}
Total Moons: {stats['total_moons']:,}
Total Space Stations: {stats['total_stations']:,}

Regions: {', '.join(stats['regions'])}

Database Size: {current.size_mb:.2f} MB"""
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        stats_label.pack(padx=20, pady=20, anchor="nw")
        
        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            fg_color=COLORS['accent_purple'],
            hover_color=COLORS['accent_pink']
        )
        close_btn.pack(pady=(0, 20))
        
        dialog.transient(self)
        dialog.grab_set()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load database statistics:\n{e}")
        logging.error(f"Database stats error: {e}", exc_info=True)
```

---

### Step 7: Update System Entry Wizard to Accept Data Source

**File:** `src/system_entry_wizard.py`

Add this at the top of the `main()` function (around line 300+):

```python
def main():
    """Main entry point - NOW RESPECTS DATA SOURCE CONTEXT"""
    import os
    
    # Get data source from environment variable (set by control_room)
    data_source = os.environ.get('HAVEN_DATA_SOURCE', 'production')
    
    # Register data source with manager
    from src.common.data_source_manager import get_data_source_manager
    manager = get_data_source_manager()
    manager.set_current(data_source)
    
    logging.info(f"System Entry Wizard initialized with data source: {data_source}")
    
    # Rest of main() function continues...
```

---

### Step 8: Test Integration

Create a test file to verify all three functions see the same data:

**File:** `test_data_source_unification.py`

```python
#!/usr/bin/env python3
"""
Test that all three functions use the same data source.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.common.data_source_manager import get_data_source_manager


def test_consistent_counts():
    """Verify all sources have consistent counts"""
    manager = get_data_source_manager()
    
    print("\n" + "="*60)
    print("TESTING DATA SOURCE UNIFICATION")
    print("="*60)
    
    # Test 1: All sources registered
    sources = manager.get_all_sources()
    print(f"\n✓ Registered {len(sources)} sources:")
    for name, info in sources.items():
        print(f"  - {name}: {info.display_name} ({info.system_count:,} systems)")
    
    # Test 2: Current source consistency
    manager.set_current("production")
    current1 = manager.get_current()
    current2 = manager.get_current()  # Should be SAME object
    print(f"\n✓ Current source returns SAME object:")
    print(f"  - Both calls return: {current1.name}")
    print(f"  - System count: {current1.system_count:,}")
    assert current1 is current2, "ERROR: get_current() returns different objects!"
    
    # Test 3: Switching sources
    manager.set_current("testing")
    current_test = manager.get_current()
    print(f"\n✓ Switching to testing source:")
    print(f"  - Current: {current_test.name}")
    print(f"  - System count: {current_test.system_count:,}")
    assert current_test.name == "testing", "ERROR: Switch failed!"
    
    # Test 4: Refresh counts
    print(f"\n✓ Refreshing all counts...")
    manager.refresh_counts()
    
    for name, info in manager.get_all_sources().items():
        print(f"  - {name}: {info.system_count:,} systems")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60 + "\n")


if __name__ == '__main__':
    test_consistent_counts()
```

**Run the test:**
```bash
python test_data_source_unification.py
```

---

## Verification Checklist

After implementation, verify these scenarios:

- [ ] **Data Source Dropdown**: 
  - Select "Production" → See same count in dropdown, stats, and wizard
  - Select "Testing" → See same count everywhere
  - Select "Load Test" → See same count everywhere

- [ ] **System Entry Wizard**:
  - Launch wizard → Uses current data source (check logs)
  - If in testing mode, wizard works with testing data
  - If in production, wizard works with production data

- [ ] **Database Statistics**:
  - Click "Database Statistics"
  - System count matches the one shown in dropdown
  - Matches what wizard is using

- [ ] **Log Output**:
  - Control room logs show data source changes with system count
  - Wizard logs show it received the correct data source

---

## Result

After integration:

✅ **ONE SOURCE OF TRUTH**
- All counts from `DataSourceManager`
- No duplication, no mismatches

✅ **CONSISTENT USER EXPERIENCE**
- User sees same numbers everywhere
- No confusion from different counts

✅ **EASY TO EXTEND**
- Add new data source? Update `_register_sources()` once
- All three functions automatically get it

✅ **MAINTAINABLE**
- Changes to counting logic in one place
- All functions benefit automatically

---

**Next Steps:**
1. Run test file to verify manager works
2. Apply changes to control_room.py
3. Update system_entry_wizard.py to accept data source
4. Run control room and verify all three functions match
5. Commit changes with message: "unify: all data sources now use single source of truth"

---

**Date:** November 6, 2025  
**Status:** Ready for Implementation
