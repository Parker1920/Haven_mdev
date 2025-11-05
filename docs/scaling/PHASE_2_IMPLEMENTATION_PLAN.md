# Phase 2 Implementation Plan: Control Room Integration

**Status:** In Progress
**Dependencies:** Phase 1 Complete ✅

---

## Overview

Phase 2 integrates the database backend with the Control Room. The Control Room will:
1. Detect and display current backend (JSON vs Database)
2. Show system statistics
3. Allow backend toggling (for testing)
4. View database statistics
5. Work seamlessly with both backends

---

## Design Philosophy

**Keep Control Room Simple:** The Control Room is a launcher/monitor, not a data editor. It should:
- Display status and statistics
- Launch tools (Wizard, Map Generator)
- Pass appropriate data source to tools
- NOT directly edit data (that's the Wizard's job)

This design minimizes changes and maintains the existing architecture.

---

## Changes Required

### 1. Add Imports (Top of file)
```python
# Add after existing imports
from config.settings import (
    USE_DATABASE, AUTO_DETECT_BACKEND,
    get_data_provider, get_current_backend,
    JSON_DATA_PATH, DATABASE_PATH,
    SHOW_BACKEND_STATUS, SHOW_SYSTEM_COUNT,
    ENABLE_DATABASE_STATS
)
```

### 2. Initialize Data Provider in `__init__`
```python
def __init__(self):
    try:
        logging.info("Creating ControlRoom window...")
        super().__init__()
        self.title("Haven Control Room")
        self.geometry("980x700")
        self.configure(fg_color=COLORS['bg_dark'])
        self._frozen = getattr(sys, 'frozen', False)

        # Data source: 'production' or 'testing'
        self.data_source = ctk.StringVar(value='production')

        # NEW: Initialize data provider
        self.data_provider = None
        self._init_data_provider()

        logging.info("Building UI...")
        self._build_ui()
        logging.info("ControlRoom initialization complete.")
    except Exception as e:
        logging.error(f"Error initializing ControlRoom: {e}", exc_info=True)
        raise

def _init_data_provider(self):
    """Initialize data provider based on configuration"""
    try:
        self.data_provider = get_data_provider()
        backend = get_current_backend()
        self.current_backend = backend
        logging.info(f"Data provider initialized: {backend}")
    except Exception as e:
        logging.error(f"Failed to initialize data provider: {e}")
        self.data_provider = None
        self.current_backend = 'json'
```

### 3. Update Status Indicator

Replace existing data indicator (line ~203-211) with enhanced version:

```python
# Enhanced data source indicator with backend info
self.data_indicator_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
self.data_indicator_frame.pack(padx=20, pady=(4, 8), fill="x")

self.data_indicator = ctk.CTkLabel(
    self.data_indicator_frame,
    text=self._get_data_indicator_text(),
    font=ctk.CTkFont(family="Segoe UI", size=10),
    text_color=COLORS['success'],
    wraplength=240,
    justify="left"
)
self.data_indicator.pack(anchor="w")

# NEW: Backend indicator (shows JSON vs Database)
if SHOW_BACKEND_STATUS:
    self.backend_indicator = ctk.CTkLabel(
        self.data_indicator_frame,
        text=f"Backend: {self.current_backend.upper()}",
        font=ctk.CTkFont(family="Segoe UI", size=9),
        text_color=COLORS['text_secondary']
    )
    self.backend_indicator.pack(anchor="w")

# NEW: System count indicator
if SHOW_SYSTEM_COUNT and self.data_provider:
    try:
        count = self.data_provider.get_total_count()
        self.count_indicator = ctk.CTkLabel(
            self.data_indicator_frame,
            text=f"Systems: {count:,}",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=COLORS['accent_cyan']
        )
        self.count_indicator.pack(anchor="w")
    except:
        pass

def _get_data_indicator_text(self):
    """Get data indicator text based on current settings"""
    source = self.data_source.get()
    if source == "testing":
        return "📊 Test Data (tests/stress_testing/TESTING.json)"
    elif self.current_backend == 'database':
        return f"📊 Production Data (Database)"
    else:
        return f"📊 Production Data (data/data.json)"
```

### 4. Add Database Statistics Viewer

Add button in Advanced Tools section (after line ~244):

```python
if not self._frozen and ENABLE_DATABASE_STATS:
    # Only show if database backend is active
    if self.current_backend == 'database':
        self._mk_btn(sidebar, "📊 Database Statistics", self.show_database_stats,
                     fg=COLORS['accent_cyan'], hover="#00b8cc").pack(padx=20, pady=4, fill="x")

def show_database_stats(self):
    """Show database statistics in a dialog"""
    if self.current_backend != 'database':
        messagebox.showinfo("Info", "Database statistics only available in database mode.")
        return

    try:
        from src.common.database import HavenDatabase
        from config.settings import DATABASE_PATH

        with HavenDatabase(str(DATABASE_PATH)) as db:
            stats = db.get_statistics()

        # Create stats dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Database Statistics")
        dialog.geometry("500x400")
        dialog.configure(fg_color=COLORS['bg_dark'])

        # Title
        title = ctk.CTkLabel(
            dialog,
            text="📊 Database Statistics",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS['accent_cyan']
        )
        title.pack(pady=20)

        # Stats frame
        stats_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS['glass'])
        stats_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Display stats
        stats_text = f"""
Total Systems: {stats['total_systems']:,}
Total Planets: {stats['total_planets']:,}
Total Moons: {stats['total_moons']:,}
Total Space Stations: {stats['total_stations']:,}

Regions: {', '.join(stats['regions'])}

Database Size: {stats['database_size_mb']:.2f} MB
Database Path: {DATABASE_PATH}
        """

        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text.strip(),
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        stats_label.pack(padx=20, pady=20)

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

### 5. Update `_on_data_source_change` Method

Enhance to update all indicators (around line 289):

```python
def _on_data_source_change(self):
    """Handle data source toggle change"""
    source = self.data_source.get()
    if source == "testing":
        self._log("Switched to TEST data source")
        self.data_indicator.configure(
            text="📊 Test Data (tests/stress_testing/TESTING.json)",
            text_color=COLORS['warning']
        )
    else:
        self._log("Switched to PRODUCTION data source")
        self.data_indicator.configure(
            text=self._get_data_indicator_text(),
            text_color=COLORS['success']
        )

    # Update system count if available
    if hasattr(self, 'count_indicator') and SHOW_SYSTEM_COUNT:
        try:
            if source == "testing":
                # Count systems in test file
                import json
                test_file = project_root() / "tests" / "stress_testing" / "TESTING.json"
                if test_file.exists():
                    with open(test_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    count = sum(1 for k, v in data.items() if k != "_meta" and isinstance(v, dict))
                    self.count_indicator.configure(text=f"Systems: {count:,}")
            else:
                count = self.data_provider.get_total_count()
                self.count_indicator.configure(text=f"Systems: {count:,}")
        except:
            pass
```

### 6. Pass Backend Info to Map Generator

Update `generate_map` method (around line 358) to pass backend info:

```python
def generate_map(self):
    """Generate the 3D star map with progress indicator."""
    # Determine which data file to use
    source = self.data_source.get()

    if source == "testing":
        data_file = project_root() / "tests" / "stress_testing" / "TESTING.json"
        self._log("Generating map with TEST data…")
    else:
        # Use appropriate backend
        if self.current_backend == 'database':
            # Map generator will detect database mode from config
            data_file = DATABASE_PATH
            self._log("Generating map with PRODUCTION data (Database)…")
        else:
            data_file = JSON_DATA_PATH
            self._log("Generating map with PRODUCTION data (JSON)…")

    # ... rest of method unchanged
```

---

## Testing Checklist

### Test with JSON Backend (USE_DATABASE = False)
- [ ] Control Room launches
- [ ] Status shows "JSON" backend
- [ ] System count displays correctly
- [ ] Data source toggle works
- [ ] Map generation works
- [ ] Wizard launches
- [ ] All existing features work

### Test with Database Backend (USE_DATABASE = True)
- [ ] Control Room launches
- [ ] Status shows "DATABASE" backend
- [ ] System count displays correctly
- [ ] Database statistics button appears
- [ ] Database statistics dialog works
- [ ] Map generation works (will need Phase 4)
- [ ] Wizard launches (will need Phase 3)

### Edge Cases
- [ ] No database file exists
- [ ] Empty database
- [ ] Large database (100+ systems)
- [ ] Corrupted database
- [ ] Missing JSON file

---

## Files to Modify

1. **src/control_room.py** - Main integration
2. **config/settings.py** - Ensure all settings correct

---

## Rollback Plan

If Phase 2 causes issues:
1. Set `USE_DATABASE = False` in config/settings.py
2. Control Room falls back to JSON mode
3. All existing functionality preserved

---

## Next Steps After Phase 2

**Phase 3:** Update System Entry Wizard to use data provider
**Phase 4:** Update Map Generator to use data provider
**Phase 5:** Add JSON import functionality to Control Room
**Phase 6:** Switch USE_DATABASE = True by default

---

## Notes

- Control Room remains a lightweight launcher
- No complex data editing in Control Room
- Wizard and Map Generator still handle data operations
- Phase 2 adds monitoring/statistics capabilities
- Backward compatibility maintained

---

*End of Phase 2 Implementation Plan*
