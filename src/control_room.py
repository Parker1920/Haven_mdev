from __future__ import annotations
import sys
import subprocess
import threading
import os
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

import customtkinter as ctk
from tkinter import messagebox, filedialog
import runpy
import argparse

from common.paths import project_root, data_dir, logs_dir, dist_dir, config_dir, docs_dir, src_dir
from common.progress import ProgressDialog, IndeterminateProgressDialog
from common.data_source_manager import get_data_source_manager
from common.vh_database_backup import backup_vh_database, cleanup_old_backups
from discoveries_window import DiscoveriesWindow

# Phase 2: Database integration imports
# Ensure project root is in sys.path so config/ can be imported
_proj_root = project_root()
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

from config.settings import (
    USE_DATABASE, AUTO_DETECT_BACKEND,
    get_data_provider, get_current_backend,
    JSON_DATA_PATH, DATABASE_PATH,
    SHOW_BACKEND_STATUS, SHOW_SYSTEM_COUNT,
    ENABLE_DATABASE_STATS
)

# Theme and colors (load from themes/haven_theme.json if available)
THEMES = {
    "Dark": ("dark", "blue"),
    "Light": ("light", "blue"),
    "Cosmic": ("dark", "green"),
    "Haven (Cyan)": ("dark", "blue"),
}

def _load_theme_colors():
    try:
        theme_path = project_root() / 'themes' / 'haven_theme.json'
        if theme_path.exists():
            import json
            obj = json.loads(theme_path.read_text(encoding='utf-8'))
            colors = obj.get('colors', {})
            return {
                'bg_dark': colors.get('bg_dark', '#0a0e27'),
                'bg_card': colors.get('bg_card', '#141b3d'),
                'accent_cyan': colors.get('accent_cyan', '#00d9ff'),
                'accent_purple': colors.get('accent_purple', '#9d4edd'),
                'accent_pink': colors.get('accent_pink', '#ff006e'),
                'text_primary': colors.get('text_primary', '#ffffff'),
                'text_secondary': colors.get('text_secondary', '#8892b0'),
                'success': colors.get('success', '#00ff88'),
                'warning': colors.get('warning', '#ffb703'),
                'error': colors.get('error', '#ff006e'),
                'glass': colors.get('glass', '#1a2342'),
                'glow': colors.get('glow', '#00ffff'),
            }
    except Exception:
        pass
    return {
        'bg_dark': '#0a0e27',
        'bg_card': '#141b3d',
        'accent_cyan': '#00d9ff',
        'accent_purple': '#9d4edd',
        'accent_pink': '#ff006e',
        'text_primary': '#ffffff',
        'text_secondary': '#8892b0',
        'success': '#00ff88',
        'warning': '#ffb703',
        'error': '#ff006e',
        'glass': '#1a2342',
        'glow': '#00ffff'
    }

COLORS = _load_theme_colors()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _setup_logging():
    logger = logging.getLogger()
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    try:
        # Create logs and error_logs directories
        logs_dir().mkdir(exist_ok=True)
        error_logs_path = logs_dir() / 'error_logs'
        error_logs_path.mkdir(exist_ok=True)

        ts = datetime.now().strftime('%Y-%m-%d')

        # Regular log file
        fh = RotatingFileHandler(logs_dir() / f'control-room-{ts}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        fh.setFormatter(fmt)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        # Error-only log file
        ts_full = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        error_fh = RotatingFileHandler(error_logs_path / f'control-room-errors-{ts_full}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        error_fh.setFormatter(fmt)
        error_fh.setLevel(logging.ERROR)
        logger.addHandler(error_fh)

        logger.info(f"Logging initialized. Error logs: {error_logs_path}")
    except Exception as e:
        print(f"Failed to setup logging: {e}", file=sys.stderr)


_setup_logging()


class GlassCard(ctk.CTkFrame):
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(
            parent,
            fg_color=(COLORS['glass'], COLORS['bg_card']),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS['accent_cyan'], COLORS['accent_cyan']),
            **kwargs
        )
        if title:
            lbl = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                text_color=COLORS['accent_cyan']
            )
            lbl.pack(pady=(16, 12), padx=20, anchor="w")


class ControlRoom(ctk.CTk):
    def __init__(self):
        try:
            logging.info("Creating ControlRoom window...")
            super().__init__()
            self.title("Haven Control Room")
            self.geometry("980x700")
            self.configure(fg_color=COLORS['bg_dark'])
            self._frozen = getattr(sys, 'frozen', False)
            # Data source: 'production', 'testing', 'load_test', or 'yh_database'
            self.data_source = ctk.StringVar(value='production')

            # Initialize VH-Database backups on startup
            self._initialize_vh_database_backups()

            # Initialize data provider
            self.data_provider = None
            self.current_backend = 'json'
            self._init_data_provider()

            logging.info("Building UI...")
            self._build_ui()
            logging.info("ControlRoom initialization complete.")
        except Exception as e:
            logging.error(f"Error initializing ControlRoom: {e}", exc_info=True)
            raise

    def _initialize_vh_database_backups(self):
        """Initialize VH-Database backups on startup"""
        try:
            vh_db_path = project_root() / "data" / "VH-Database.db"
            
            # Only backup if YH-Database exists
            if vh_db_path.exists():
                logging.info("Creating backup of VH-Database on startup...")
                backup_path = backup_vh_database(vh_db_path)
                
                if backup_path:
                    logging.info(f"✓ Backup created: {backup_path.name}")
                    
                    # Clean up old backups, keep last 10
                    deleted = cleanup_old_backups(keep_count=10)
                    if deleted > 0:
                        logging.info(f"Cleaned up {deleted} old backups")
                else:
                    logging.warning("Failed to create backup of VH-Database")
            else:
                logging.debug("VH-Database not found, skipping backup")
        
        except Exception as e:
            logging.error(f"Error initializing VH-Database backups: {e}")

    def _init_data_provider(self):
        """Initialize data provider based on configuration (Phase 2)"""
        try:
            self.data_provider = get_data_provider()
            self.current_backend = get_current_backend()
            logging.info(f"Data provider initialized: {self.current_backend}")
            
            # Check data sync status on startup
            self._check_data_sync_status()
        except Exception as e:
            logging.error(f"Failed to initialize data provider: {e}")
            self.data_provider = None
            self.current_backend = 'json'

    def _check_data_sync_status(self):
        """Check if JSON and database are in sync (Phase 2)"""
        try:
            from src.migration.sync_data import DataSynchronizer
            syncer = DataSynchronizer()
            status = syncer.check_sync_status()
            
            if "error" in status:
                logging.warning(f"Could not check sync status: {status['error']}")
                return
            
            if not status['in_sync']:
                msg = f"Data sync issue detected: "
                issues = []
                if status['only_in_json'] > 0:
                    issues.append(f"{status['only_in_json']} systems only in JSON")
                if status['only_in_db'] > 0:
                    issues.append(f"{status['only_in_db']} systems only in database")
                if status['differences'] > 0:
                    issues.append(f"{status['differences']} systems differ")
                msg += ", ".join(issues)
                logging.warning(msg)
                
                # Store sync status for UI to show if needed
                self.sync_status = status
            else:
                logging.info(f"Data sync OK: JSON and database both have {status['json_count']} systems")
                self.sync_status = None
        except Exception as e:
            logging.debug(f"Sync check failed (non-critical): {e}")

    # -------------------------- UI --------------------------
    def _build_ui(self):
        sidebar = ctk.CTkFrame(self, width=280, fg_color=COLORS['glass'], corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        title = ctk.CTkLabel(sidebar, text="✨ HAVEN\nCONTROL ROOM", justify="center",
                              font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                              text_color=COLORS['accent_cyan'])
        title.pack(pady=(32, 20))

        ctk.CTkFrame(sidebar, height=2, fg_color=COLORS['accent_cyan']).pack(fill="x", padx=20, pady=(0, 20))

        # Quick Actions section
        quick_label = ctk.CTkLabel(sidebar, text="QUICK ACTIONS",
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                   text_color=COLORS['text_secondary'])
        quick_label.pack(padx=20, pady=(0, 8), anchor="w")

        # Use high-contrast dark buttons with light text for readability
        qa_fg = "#1e3a5f"      # deep blue
        qa_hover = "#2a4a7c"   # lighter blue
        self._mk_btn(sidebar, "🛰️ Launch System Entry (Wizard)", self.launch_gui,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🗺️ Generate Map", self.generate_map,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🌐 Open Latest Map", self.open_latest_map,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # Data Source section
        data_label = ctk.CTkLabel(sidebar, text="DATA SOURCE",
                                  font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                  text_color=COLORS['text_secondary'])
        data_label.pack(padx=20, pady=(0, 8), anchor="w")

        # Data source dropdown (professional menu)
        data_dropdown_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        data_dropdown_frame.pack(padx=20, pady=(0, 4), fill="x")

        # Get available data sources dynamically from DataSourceManager
        manager = get_data_source_manager()
        available_sources = list(manager.get_all_sources().keys())

        self.data_dropdown = ctk.CTkOptionMenu(
            data_dropdown_frame,
            variable=self.data_source,
            values=available_sources,  # Dynamic from DataSourceManager
            command=self._on_data_source_change,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS['glass'],
            button_color=COLORS['accent_purple'],
            button_hover_color=COLORS['accent_cyan'],
            dropdown_fg_color=COLORS['glass'],
            dropdown_hover_color=COLORS['accent_purple'],
            text_color=COLORS['text_primary'],
            width=240,
            height=36,
            corner_radius=8
        )
        self.data_dropdown.pack(fill="x")
        
        # Descriptive label for selected data source
        self.data_description = ctk.CTkLabel(
            data_dropdown_frame,
            text=self._get_data_source_description(),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS['text_secondary'],
            wraplength=240,
            justify="left"
        )
        self.data_description.pack(anchor="w", pady=(4, 0))

        # Phase 2: Enhanced data source indicator with backend info
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

        # Backend indicator (shows JSON vs Database)
        if SHOW_BACKEND_STATUS:
            self.backend_indicator = ctk.CTkLabel(
                self.data_indicator_frame,
                text=f"Backend: {self.current_backend.upper()}",
                font=ctk.CTkFont(family="Segoe UI", size=9),
                text_color=COLORS['text_secondary']
            )
            self.backend_indicator.pack(anchor="w")

        # System count indicator
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
            except Exception as e:
                logging.warning(f"Failed to get system count: {e}")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # File Management section
        files_label = ctk.CTkLabel(sidebar, text="FILE MANAGEMENT",
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                   text_color=COLORS['text_secondary'])
        files_label.pack(padx=20, pady=(0, 8), anchor="w")

        self._mk_btn(sidebar, "📁 Data Folder", lambda: self.open_path(data_dir()),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🧭 Logs Folder", lambda: self.open_path(logs_dir()),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "📖 Documentation", lambda: self.open_path(docs_dir()),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # Advanced Tools section - hidden in standalone EXE
        if not self._frozen:
            advanced_label = ctk.CTkLabel(sidebar, text="ADVANCED TOOLS",
                                          font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                          text_color=COLORS['text_secondary'])
            advanced_label.pack(padx=20, pady=(0, 8), anchor="w")

            self._mk_btn(sidebar, "🔧 Update Dependencies", self.update_deps,
                         fg=COLORS['accent_purple'], hover=COLORS['accent_pink']).pack(padx=20, pady=4, fill="x")
            # Export button opens a small modal to choose platform and output folder
            self._mk_btn(sidebar, "📦 Export App (EXE/.app)", self.open_export_dialog,
                         fg=COLORS['warning'], hover="#cc9602").pack(padx=20, pady=4, fill="x")
            # System Test button opens interactive menu
            self._mk_btn(sidebar, "🧪 System Test", self.show_system_test_menu,
                         fg=COLORS['accent_cyan'], hover="#00b8cc").pack(padx=20, pady=4, fill="x")

            # Database Statistics button (only show if database backend active)
            if ENABLE_DATABASE_STATS and self.current_backend == 'database':
                self._mk_btn(sidebar, "📊 Database Statistics", self.show_database_stats,
                             fg=COLORS['accent_cyan'], hover="#00b8cc").pack(padx=20, pady=4, fill="x")

            # Data Sync button (show if both JSON and database exist)
            self._mk_btn(sidebar, "🔄 Sync Data (JSON ↔ DB)", self.show_sync_dialog,
                         fg=COLORS['accent_purple'], hover=COLORS['accent_pink']).pack(padx=20, pady=4, fill="x")
            
            # Phase 5: JSON Import button (import external JSON files)
            self._mk_btn(sidebar, "📥 Import JSON File", self.show_import_json_dialog,
                         fg=COLORS['success'], hover="#009966").pack(padx=20, pady=4, fill="x")

        # Content area
        content = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.status_card = GlassCard(content, title="📡 System Status")
        self.status_card.pack(fill="both", expand=True)

        self.status_label = ctk.CTkLabel(self.status_card, text="Ready.",
                                         font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                         text_color=COLORS['accent_cyan'])
        self.status_label.pack(padx=24, pady=(0, 12), anchor="w")

        self.log_box = ctk.CTkTextbox(self.status_card, height=500, corner_radius=12,
                                      border_width=1, border_color=COLORS['accent_cyan'],
                                      fg_color=COLORS['bg_dark'],
                                      text_color=COLORS['text_primary'],
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(padx=24, pady=(0, 24), fill="both", expand=True)
        self._log_ui("Control Room initialized.")

    def _mk_btn(self, parent, text, cmd, fg=COLORS['bg_card'], hover=COLORS['glass'], text_color=COLORS['text_primary']):
        return ctk.CTkButton(
            parent,
            text=text,
            command=cmd,
            height=40,
            corner_radius=10,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )

    # ----------------------- Utilities ----------------------
    def _get_data_indicator_text(self):
        """Get data indicator text - NOW UNIFIED via DataSourceManager"""
        manager = get_data_source_manager()
        current = manager.get_current()
        
        if current:
            return f"{current.icon} {current.display_name}"
        return "📊 Unknown Data Source"
    
    def _get_data_source_description(self):
        """Get descriptive text for current data source - NOW UNIFIED"""
        manager = get_data_source_manager()
        source = self.data_source.get()
        source_info = manager.get_source(source)
        
        if source_info:
            return source_info.description
        return ""

    def _log(self, msg: str):
        logging.info(msg)
        self._log_ui(msg)

    def _log_ui(self, msg: str):
        self.log_box.insert('end', f"{msg}\n")
        self.log_box.see('end')
        self.status_label.configure(text=msg)

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


    def _confirm(self, title: str, msg: str) -> bool:
        return messagebox.askyesno(title, msg)

    def open_path(self, path: Path):
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', str(path)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(path)])
            else:
                subprocess.Popen(['xdg-open', str(path)])
            self._log(f"Opened: {path}")
        except Exception as e:
            self._log(f"Failed to open path: {e}")

    def _run_bg(self, target, *args, **kwargs):
        t = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t

    # ----------------------- Actions ------------------------
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
                    # Relaunch the same EXE with data source context
                    cmd = [sys.executable, '--entry', 'system', '--data-source', current_source.name]
                    subprocess.Popen(cmd, cwd=str(project_root()))
                else:
                    app = src_dir() / 'system_entry_wizard.py'
                    env = os.environ.copy()
                    env['HAVEN_DATA_SOURCE'] = current_source.name
                    
                    if sys.platform == 'darwin':
                        # macOS: Create temp shell script with env var
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

    def generate_map(self):
        """Generate the 3D star map with progress indicator."""
        # Determine which data file to use
        source = self.data_source.get()
        if source == "testing":
            data_file = project_root() / "tests" / "stress_testing" / "TESTING.json"
            self._log("Generating map with TEST data (500 systems)…")
        elif source == "load_test":
            data_file = project_root() / "data" / "haven_load_test.db"
            # Check if load test database exists
            if not data_file.exists():
                self._log("⚠️ Load test database not found. Run generate_load_test_db.py first.")
                return
            self._log("Generating map with LOAD TEST database…")
        else:
            data_file = project_root() / "data" / "data.json"
            self._log("Generating map with PRODUCTION data…")

        # Show progress dialog
        progress = IndeterminateProgressDialog(
            self,
            "Generating Map",
            "Preparing map data..."
        )

        def run():
            try:
                ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                logs_dir().mkdir(exist_ok=True)

                # Update progress message
                self.after(100, lambda: progress.set_message("Generating 3D visualization..."))

                if self._frozen:
                    # Spawn same EXE to run the map generator entry
                    with open(logs_dir() / f'map-gen-{ts}.log', 'w', encoding='utf-8') as lf:
                        cmd = [sys.executable, '--entry', 'map', '--no-open', '--data-file', str(data_file)]
                        proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                else:
                    map_script = src_dir() / 'Beta_VH_Map.py'
                    with open(logs_dir() / f'map-gen-{ts}.log', 'w', encoding='utf-8') as lf:
                        cmd = [sys.executable, str(map_script), '--no-open', '--data-file', str(data_file)]
                        proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)

                # Close progress dialog
                self.after(0, progress.close_dialog)

                if proc.returncode == 0:
                    self._log("✓ Map generation complete.")
                else:
                    self._log(f"✗ Map generation failed (exit {proc.returncode}). See logs.")
            except Exception as e:
                self.after(0, progress.close_dialog)
                self._log(f"Map generation error: {e}")

        self._run_bg(run)

    def open_latest_map(self):
        try:
            dist = dist_dir()
            if not dist.exists():
                self._log("No dist folder yet.")
                return
            # Prefer VH-Map.html
            vh = dist / 'VH-Map.html'
            target = vh if vh.exists() else None
            if not target:
                # fallback to newest html file
                htmls = sorted(dist.glob('*.html'), key=lambda p: p.stat().st_mtime, reverse=True)
                target = htmls[0] if htmls else None
            if not target:
                self._log("No map HTML found in dist/.")
                return
            if sys.platform == 'win32':
                subprocess.Popen(['cmd', '/c', 'start', '', str(target)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(target)])
            else:
                subprocess.Popen(['xdg-open', str(target)])
            self._log(f"Opened: {target.name}")
        except Exception as e:
            self._log(f"Failed to open map: {e}")

    def update_deps(self):
        if self._frozen:
            self._log("Dependency updates are unavailable in the standalone EXE.")
            return
        if not self._confirm("Update Dependencies", "Run pip install -r config/requirements.txt?\nThis may take a few minutes."):
            return
        self._log("Updating dependencies…")
        def run():
            try:
                req = config_dir() / 'requirements.txt'
                cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(req)]
                ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                with open(logs_dir() / f'update-deps-{ts}.log', 'w', encoding='utf-8') as lf:
                    proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                if proc.returncode == 0:
                    self._log("Dependencies updated.")
                else:
                    self._log(f"Dependency update failed (exit {proc.returncode}). See logs.")
            except Exception as e:
                self._log(f"Update error: {e}")
        self._run_bg(run)

    def open_export_dialog(self):
        if self._frozen:
            self._log("Export is not available from within the standalone app. Run from source to export.")
            return
        ExportDialog(self)

    def _export_windows(self, output_dir: Path, zip_after: bool = True):
        self._log(f"Exporting Windows EXE to: {output_dir}")
        def run():
            try:
                name = 'HavenControlRoom'
                script = src_dir() / 'control_room.py'
                icon = (config_dir() / 'icons' / 'haven.ico')
                spec_dir = config_dir() / 'pyinstaller'
                try:
                    spec_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                # Use a temp work path outside OneDrive to avoid file locking
                import tempfile, shutil
                workpath = Path(tempfile.gettempdir()) / 'haven_build_win'
                try:
                    if workpath.exists():
                        shutil.rmtree(workpath, ignore_errors=True)
                except Exception:
                    pass
                # Best effort: remove repo build folder if present
                try:
                    repo_build = project_root() / 'build'
                    if repo_build.exists():
                        shutil.rmtree(repo_build, ignore_errors=True)
                except Exception:
                    pass
                # Ensure output dir exists and direct distpath there
                output_dir.mkdir(parents=True, exist_ok=True)
                # Build command with hidden imports for packaged entries
                cmd = [
                    sys.executable, '-m', 'PyInstaller',
                    '--noconfirm', '--clean', '--windowed', '--onefile',
                    '--name', name,
                    '--specpath', str(spec_dir),
                    '--workpath', str(workpath),
                    '--distpath', str(output_dir),
                    '--hidden-import', 'system_entry_wizard',
                    '--hidden-import', 'Beta_VH_Map',
                    str(script)
                ]
                if icon.exists():
                    cmd[ cmd.index('--onefile')+1:cmd.index('--onefile')+1 ] = ['--icon', str(icon)]
                ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                build_log = logs_dir() / f'export-windows-{ts}.log'
                with open(build_log, 'w', encoding='utf-8') as lf:
                    proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                if proc.returncode != 0:
                    self._log(f"Windows export failed (exit {proc.returncode}). See {build_log.name}")
                    return
                exe = output_dir / f'{name}.exe'
                if not exe.exists():
                    self._log("Build finished, but EXE not found. See logs.")
                    return
                # Optional ZIP with instructions for email
                if zip_after:
                    import shutil, tempfile
                    readme_text = (
                        "Haven Control Room (Windows)\r\n\r\n"
                        "Run: Double-click HavenControlRoom.exe\r\n"
                        "Notes: Windows may show a SmartScreen prompt. Click 'More info' > 'Run anyway'.\r\n"
                    )
                    tmpdir = Path(tempfile.mkdtemp())
                    (tmpdir / 'HavenControlRoom.exe').write_bytes(exe.read_bytes())
                    (tmpdir / 'README.txt').write_text(readme_text, encoding='utf-8')
                    zip_path = output_dir / f'HavenControlRoom_Windows_{ts}.zip'
                    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', str(tmpdir))
                self._log(f"Windows export complete: {exe}")
            except Exception as e:
                self._log(f"Windows export error: {e}")
        self._run_bg(run)

    def _export_macos(self, output_dir: Path):
        # Building macOS app requires running on macOS
        if sys.platform != 'darwin':
            self._log("Cannot build macOS app on this OS. Generating a Mac Build Kit ZIP with instructions.")
            def run():
                try:
                    import tempfile, shutil
                    ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                    kit_dir = Path(tempfile.mkdtemp()) / 'Haven_Mac_BuildKit'
                    kit_dir.mkdir(parents=True, exist_ok=True)
                    # Instructions
                    instr = (
                        "# Haven Mac Build Kit\n\n"
                        "Requirements: macOS with Python 3.11+, pip, and PyInstaller installed.\n\n"
                        "Build steps:\n"
                        "1) python3 -m pip install --upgrade pip\n"
                        "2) python3 -m pip install pyinstaller\n"
                        "3) python3 -m PyInstaller --noconfirm --clean --windowed --onefile \n"
                        "   --name HavenControlRoom --hidden-import system_entry_wizard --hidden-import Beta_VH_Map \n"
                        "   src/control_room.py\n\n"
                        "Output: dist/HavenControlRoom (macOS app).\n"
                    )
                    (kit_dir / 'MAC_BUILD_INSTRUCTIONS.md').write_text(instr, encoding='utf-8')
                    # Include minimal project needed to build
                    root = project_root()
                    # Copy src, config (icons), and a tiny README
                    for folder in ('src', 'config'):
                        src_path = root / folder
                        if src_path.exists():
                            shutil.copytree(src_path, kit_dir / folder, dirs_exist_ok=True)
                    (kit_dir / 'README.txt').write_text('Use MAC_BUILD_INSTRUCTIONS.md to build the macOS app.', encoding='utf-8')
                    output_dir.mkdir(parents=True, exist_ok=True)
                    zip_path = output_dir / f'HavenControlRoom_Mac_BuildKit_{ts}.zip'
                    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', str(kit_dir))
                    self._log(f"Mac Build Kit created: {zip_path}")
                except Exception as e:
                    self._log(f"Mac export error: {e}")
            self._run_bg(run)
            return
        else:
            # On macOS, attempt to build the app
            self._log(f"Exporting macOS app to: {output_dir}")
            def run():
                try:
                    name = 'HavenControlRoom'
                    script = src_dir() / 'control_room.py'
                    icon = (config_dir() / 'icons' / 'haven.icns')
                    spec_dir = config_dir() / 'pyinstaller'
                    try:
                        spec_dir.mkdir(parents=True, exist_ok=True)
                    except Exception:
                        pass
                    import tempfile, shutil
                    workpath = Path(tempfile.gettempdir()) / 'haven_build_mac'
                    try:
                        if workpath.exists():
                            shutil.rmtree(workpath, ignore_errors=True)
                    except Exception:
                        pass
                    output_dir.mkdir(parents=True, exist_ok=True)
                    cmd = [
                        sys.executable, '-m', 'PyInstaller',
                        '--noconfirm', '--clean', '--windowed', '--onefile',
                        '--name', name,
                        '--specpath', str(spec_dir),
                        '--workpath', str(workpath),
                        '--distpath', str(output_dir),
                        '--hidden-import', 'system_entry_wizard',
                        '--hidden-import', 'Beta_VH_Map',
                        str(script)
                    ]
                    if icon.exists():
                        cmd[ cmd.index('--onefile')+1:cmd.index('--onefile')+1 ] = ['--icon', str(icon)]
                    ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                    build_log = logs_dir() / f'export-macos-{ts}.log'
                    with open(build_log, 'w', encoding='utf-8') as lf:
                        proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                    if proc.returncode != 0:
                        self._log(f"macOS export failed (exit {proc.returncode}). See {build_log.name}")
                        return
                    app = output_dir / name
                    self._log(f"macOS export complete: {app}")
                except Exception as e:
                    self._log(f"macOS export error: {e}")
            self._run_bg(run)

    def show_system_test_menu(self):
        """Open the System Test menu modal."""
        SystemTestMenu(self)

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

    def show_sync_dialog(self):
        """Show data synchronization dialog (Phase 2)"""
        try:
            from src.migration.sync_data import DataSynchronizer
            
            dialog = ctk.CTkToplevel(self)
            dialog.geometry("700x600")
            dialog.title("Data Synchronization")
            dialog.configure(fg_color=COLORS['bg_dark'])

            # Title
            title = ctk.CTkLabel(
                dialog,
                text="🔄 Data Synchronization",
                font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                text_color=COLORS['accent_cyan']
            )
            title.pack(pady=(20, 10))

            # Check sync status
            syncer = DataSynchronizer()
            status = syncer.check_sync_status()

            if "error" in status:
                error_label = ctk.CTkLabel(
                    dialog,
                    text=f"Error checking sync status:\n{status['error']}",
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=COLORS['error']
                )
                error_label.pack(pady=20)
                return

            # Status frame
            status_frame = ctk.CTkFrame(dialog, fg_color=COLORS['glass'])
            status_frame.pack(fill="x", padx=20, pady=10)

            # Build status text
            status_text = f"""JSON File: {status['json_count']} systems
Database: {status['db_count']} systems
In Both: {status['in_both']} systems

Status: {'✓ IN SYNC' if status['in_sync'] else '✗ OUT OF SYNC'}"""

            if not status['in_sync']:
                if status['only_in_json'] > 0:
                    status_text += f"\n\n⚠ {status['only_in_json']} systems only in JSON"
                if status['only_in_db'] > 0:
                    status_text += f"\n⚠ {status['only_in_db']} systems only in database"
                if status['differences'] > 0:
                    status_text += f"\n⚠ {status['differences']} systems have differences"

            status_label = ctk.CTkLabel(
                status_frame,
                text=status_text,
                font=ctk.CTkFont(family="Consolas", size=12),
                text_color=COLORS['success'] if status['in_sync'] else COLORS['warning'],
                justify="left"
            )
            status_label.pack(padx=20, pady=20)

            # Action buttons frame
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(pady=20)

            # JSON to DB button
            def sync_json_to_db():
                if messagebox.askyesno("Confirm", "Sync database from JSON?\n\nThis will add any systems in JSON to the database."):
                    try:
                        success = syncer.sync_json_to_db(overwrite=False)
                        if success:
                            messagebox.showinfo("Success", "Database synced from JSON")
                            dialog.destroy()
                            self._check_data_sync_status()  # Re-check status
                        else:
                            messagebox.showerror("Error", "Sync failed. Check logs for details.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Sync failed: {e}")

            json_to_db_btn = ctk.CTkButton(
                btn_frame,
                text="JSON → Database",
                command=sync_json_to_db,
                fg_color=COLORS['accent_cyan'],
                hover_color="#00b8cc",
                width=180
            )
            json_to_db_btn.grid(row=0, column=0, padx=10, pady=5)

            # DB to JSON button
            def sync_db_to_json():
                if messagebox.askyesno("Confirm", "Sync JSON from database?\n\nThis will overwrite data.json with database contents.\n\nA backup will be created."):
                    try:
                        success = syncer.sync_db_to_json(backup=True)
                        if success:
                            messagebox.showinfo("Success", "JSON synced from database")
                            dialog.destroy()
                            self._check_data_sync_status()  # Re-check status
                        else:
                            messagebox.showerror("Error", "Sync failed. Check logs for details.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Sync failed: {e}")

            db_to_json_btn = ctk.CTkButton(
                btn_frame,
                text="Database → JSON",
                command=sync_db_to_json,
                fg_color=COLORS['accent_purple'],
                hover_color=COLORS['accent_pink'],
                width=180
            )
            db_to_json_btn.grid(row=0, column=1, padx=10, pady=5)

            # Info text
            info_text = """
Synchronization Options:

• JSON → Database: Copies systems from JSON to database
  (Keeps existing database systems)

• Database → JSON: Copies systems from database to JSON
  (Overwrites JSON file, creates backup)

Use these tools to keep your data in sync when switching
between JSON and database backends.
            """

            info_label = ctk.CTkLabel(
                dialog,
                text=info_text.strip(),
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS['text_secondary'],
                justify="left"
            )
            info_label.pack(padx=30, pady=10)

            # Close button
            close_btn = ctk.CTkButton(
                dialog,
                text="Close",
                command=dialog.destroy,
                fg_color=COLORS['bg_card'],
                hover_color=COLORS['glass']
            )
            close_btn.pack(pady=(10, 20))

            dialog.transient(self)
            dialog.grab_set()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open sync dialog:\n{e}")
            logging.error(f"Sync dialog error: {e}", exc_info=True)

    def show_import_json_dialog(self):
        """Show JSON import dialog (Phase 5)"""
        try:
            # File dialog to select JSON file
            file_path = filedialog.askopenfilename(
                title="Select JSON File to Import",
                initialdir=data_dir() / "imports",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file_path:
                return  # User cancelled
            
            file_path = Path(file_path)
            
            # Create progress dialog
            dialog = ctk.CTkToplevel(self)
            dialog.geometry("600x500")
            dialog.title("Import JSON File")
            dialog.configure(fg_color=COLORS['bg_dark'])
            
            # Title
            title = ctk.CTkLabel(
                dialog,
                text="📥 Import JSON File",
                font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                text_color=COLORS['success']
            )
            title.pack(pady=(20, 10))
            
            # File info
            file_info = ctk.CTkLabel(
                dialog,
                text=f"File: {file_path.name}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS['text_secondary']
            )
            file_info.pack(pady=5)
            
            # Options frame
            options_frame = ctk.CTkFrame(dialog, fg_color=COLORS['glass'])
            options_frame.pack(fill="x", padx=20, pady=15)
            
            # Update existing systems checkbox
            update_var = ctk.BooleanVar(value=False)
            update_check = ctk.CTkCheckBox(
                options_frame,
                text="Update existing systems (if False, duplicates will be skipped)",
                variable=update_var,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS['text_primary']
            )
            update_check.pack(padx=20, pady=15)
            
            # Result text area
            result_frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_card'])
            result_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            result_text = ctk.CTkTextbox(
                result_frame,
                font=ctk.CTkFont(family="Consolas", size=10),
                fg_color=COLORS['bg_card'],
                text_color=COLORS['text_primary']
            )
            result_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            def do_import():
                """Perform the import"""
                try:
                    result_text.delete("1.0", "end")
                    result_text.insert("1.0", f"Importing from {file_path.name}...\n\n")
                    dialog.update()
                    
                    # Import using JSONImporter
                    from src.migration.import_json import JSONImporter
                    
                    importer = JSONImporter(use_database=USE_DATABASE)
                    allow_updates = update_var.get()
                    
                    # Redirect output to text widget
                    import io
                    output_buffer = io.StringIO()
                    
                    class OutputRedirector:
                        def write(self, text):
                            result_text.insert("end", text)
                            dialog.update()
                        def flush(self):
                            pass
                    
                    old_stdout = sys.stdout
                    sys.stdout = OutputRedirector()
                    
                    success = importer.import_file(file_path, allow_updates=allow_updates)
                    
                    sys.stdout = old_stdout
                    
                    if success:
                        result_text.insert("end", "\n\n✅ IMPORT SUCCESSFUL!\n")
                        result_text.insert("end", f"Imported: {importer.stats.systems_imported}\n")
                        result_text.insert("end", f"Updated: {importer.stats.systems_updated}\n")
                        result_text.insert("end", f"Skipped: {importer.stats.systems_skipped}\n")
                        result_text.insert("end", f"Failed: {importer.stats.systems_failed}\n")
                        
                        # Refresh UI if we have a data provider
                        if self.data_provider:
                            self._refresh_backend_info()
                    else:
                        result_text.insert("end", "\n\n❌ IMPORT FAILED\n")
                        result_text.insert("end", f"Check errors above for details.\n")
                    
                except Exception as e:
                    result_text.insert("end", f"\n\n❌ ERROR: {e}\n")
                    logging.error(f"Import error: {e}", exc_info=True)
            
            # Button frame
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(pady=10)
            
            import_btn = ctk.CTkButton(
                btn_frame,
                text="Import",
                command=do_import,
                fg_color=COLORS['success'],
                hover_color="#009966",
                width=120
            )
            import_btn.pack(side="left", padx=5)
            
            close_btn = ctk.CTkButton(
                btn_frame,
                text="Close",
                command=dialog.destroy,
                fg_color=COLORS['bg_card'],
                hover_color=COLORS['glass'],
                width=120
            )
            close_btn.pack(side="left", padx=5)
            
            dialog.transient(self)
            dialog.grab_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open import dialog:\n{e}")
            logging.error(f"Import dialog error: {e}", exc_info=True)

    # ==================== Export Dialog ====================

    # iOS PWA export removed - archived in Archive-Dump
    # Use Haven_Mobile_Map.html instead (located in dist/ folder)


class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent: ControlRoom):
        super().__init__(parent)
        self.title("Export Application")
        self.geometry("480x260")
        self.configure(fg_color=COLORS['bg_card'])
        self.parent = parent
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="Choose platform and output folder:",
                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                     text_color=COLORS['text_primary']).pack(pady=(20,10))

        self.platform_var = ctk.StringVar(value='Windows')
        options = ctk.CTkOptionMenu(
            self,
            values=['Windows', 'macOS'],
            variable=self.platform_var,
            fg_color=COLORS['glass'],
            button_color=COLORS['accent_cyan'],
            text_color=COLORS['text_primary']
        )
        options.pack(pady=6)

        path_frame = ctk.CTkFrame(self, fg_color='transparent')
        path_frame.pack(fill='x', padx=20, pady=10)
        self.path_var = ctk.StringVar(value=str(dist_dir()))
        entry = ctk.CTkEntry(path_frame, textvariable=self.path_var, width=320)
        entry.pack(side='left', padx=(0,10))
        browse = ctk.CTkButton(
            path_frame,
            text='Browse…',
            command=self._pick_dir,
            fg_color=COLORS['accent_cyan'],
            text_color=COLORS['bg_dark']
        )
        browse.pack(side='left')

        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(pady=20)
        ctk.CTkButton(btns, text='Cancel', command=self.destroy, width=120,
                      fg_color=COLORS['glass']).pack(side='left', padx=10)
        ctk.CTkButton(btns, text='Export', command=self._export, width=160,
                      fg_color=COLORS['warning']).pack(side='left', padx=10)

    def _pick_dir(self):
        d = filedialog.askdirectory(title='Choose export output folder')
        if d:
            self.path_var.set(d)

    def _export(self):
        out = Path(self.path_var.get()).expanduser()
        platform = self.platform_var.get()
        if platform == 'Windows':
            self.parent._export_windows(out, zip_after=True)
        elif platform == 'macOS':
            self.parent._export_macos(out)
        self.destroy()


class SystemTestMenu(ctk.CTkToplevel):
    """Interactive System Test Menu - run tests from the Control Room."""
    
    def __init__(self, parent: ControlRoom):
        super().__init__(parent)
        self.title("🧪 System Test Menu")
        self.geometry("700x650")
        self.configure(fg_color=COLORS['bg_card'])
        self.parent = parent
        self.resizable(True, True)
        self.grab_set()
        
        # Import test suite
        from common.system_tests import get_test_suite
        self.test_suite = get_test_suite(project_root())
        self.selected_tests = []
        self.test_checkboxes = {}
        self.results_visible = False
        
        # ===================== HEADER =====================
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(header, text="🧪 System Test Suite",
                            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                            text_color=COLORS['accent_cyan'])
        title.pack(anchor="w")
        
        desc = ctk.CTkLabel(header, text="Run validation, security, unit, and stress tests",
                           font=ctk.CTkFont(family="Segoe UI", size=12),
                           text_color=COLORS['text_secondary'])
        desc.pack(anchor="w", pady=(4, 0))
        
        # ===================== TEST SELECTION =====================
        select_frame = ctk.CTkFrame(self, fg_color='transparent')
        select_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        select_label = ctk.CTkLabel(select_frame, text="SELECT TESTS",
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                   text_color=COLORS['text_secondary'])
        select_label.pack(anchor="w")
        
        # Quick selection buttons
        quick_frame = ctk.CTkFrame(self, fg_color='transparent')
        quick_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkButton(quick_frame, text="Select All", command=self._select_all, width=80,
                     fg_color=COLORS['accent_cyan'], text_color=COLORS['bg_dark'],
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=4)
        ctk.CTkButton(quick_frame, text="Clear All", command=self._clear_all, width=80,
                     fg_color=COLORS['glass'],
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=4)
        ctk.CTkButton(quick_frame, text="Validation Only", command=lambda: self._select_category("validation"),
                     width=120, fg_color="#1e3a5f",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=4)
        ctk.CTkButton(quick_frame, text="Security Only", command=lambda: self._select_category("security"),
                     width=120, fg_color="#5f1e3a",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=4)
        
        # ===================== TEST SCROLLABLE LIST =====================
        list_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_dark'],
                                           corner_radius=12, border_width=1,
                                           border_color=COLORS['accent_cyan'])
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Organize tests by category
        for category in sorted(self.test_suite.tests.keys()):
            tests = self.test_suite.tests[category]
            if not tests:
                continue
            
            # Category header
            cat_frame = ctk.CTkFrame(list_frame, fg_color='transparent')
            cat_frame.pack(fill="x", padx=15, pady=(12, 8), anchor="w")
            
            icons = {"validation": "✅", "unit": "🔬", "security": "🔒", "stress": "⚡"}
            icon = icons.get(category, "📝")
            
            cat_label = ctk.CTkLabel(cat_frame, text=f"{icon} {category.upper()} ({len(tests)})",
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    text_color=COLORS['accent_cyan'])
            cat_label.pack(anchor="w")
            
            # Tests in category
            for test in tests:
                test_frame = ctk.CTkFrame(list_frame, fg_color=COLORS['bg_card'], corner_radius=8)
                test_frame.pack(fill="x", padx=15, pady=4)
                
                var = ctk.BooleanVar(value=False)
                self.test_checkboxes[test.name] = (var, test)
                
                cb = ctk.CTkCheckBox(test_frame, text="", variable=var,
                                    fg_color=COLORS['accent_cyan'],
                                    checkmark_color=COLORS['bg_dark'],
                                    border_color=COLORS['accent_cyan'])
                cb.pack(side="left", padx=12, pady=10)
                
                info_frame = ctk.CTkFrame(test_frame, fg_color='transparent')
                info_frame.pack(side="left", fill="both", expand=True, padx=0, pady=8)
                
                name_label = ctk.CTkLabel(info_frame, text=test.name,
                                         font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                         text_color=COLORS['text_primary'])
                name_label.pack(anchor="w")
                
                desc_label = ctk.CTkLabel(info_frame, text=test.description,
                                         font=ctk.CTkFont(family="Segoe UI", size=10),
                                         text_color=COLORS['text_secondary'])
                desc_label.pack(anchor="w", padx=(0, 10))
        
        # ===================== RESULTS AREA (Hidden by default) =====================
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_dark'],
                                                    corner_radius=12, border_width=1,
                                                    border_color=COLORS['accent_cyan'])
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.results_frame.pack_forget()  # Hidden initially
        
        # ===================== ACTION BUTTONS =====================
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, width=120,
                     fg_color=COLORS['glass']).pack(side="right", padx=10)
        
        ctk.CTkButton(btn_frame, text="Run Tests", command=self._run_selected_tests, width=160,
                     fg_color=COLORS['accent_cyan'], text_color=COLORS['bg_dark'],
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=10)
    
    def _select_all(self):
        """Select all tests."""
        for var, _ in self.test_checkboxes.values():
            var.set(True)
    
    def _clear_all(self):
        """Clear all selections."""
        for var, _ in self.test_checkboxes.values():
            var.set(False)
    
    def _select_category(self, category: str):
        """Select all tests in a category."""
        self._clear_all()
        for name, (var, test) in self.test_checkboxes.items():
            if test.category == category:
                var.set(True)
    
    def _run_selected_tests(self):
        """Run selected tests and display results."""
        # Get selected tests
        selected = [(name, test) for name, (var, test) in self.test_checkboxes.items()
                   if var.get()]
        
        if not selected:
            messagebox.showwarning("No Tests Selected", "Please select at least one test to run.")
            return
        
        # Show results area, hide test list
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.results_visible = True
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Run tests
        passed = 0
        failed = 0
        
        for name, test in selected:
            # Result frame
            result_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS['bg_card'], corner_radius=8)
            result_frame.pack(fill="x", padx=15, pady=6)
            
            # Run test
            success, output, error = test.run()
            
            if success:
                passed += 1
                status_icon = "✅"
                status_color = COLORS['success']
            else:
                failed += 1
                status_icon = "❌"
                status_color = COLORS['error']
            
            # Header with status
            header_frame = ctk.CTkFrame(result_frame, fg_color='transparent')
            header_frame.pack(fill="x", padx=12, pady=(10, 4), anchor="w")
            
            status_label = ctk.CTkLabel(header_frame, text=f"{status_icon} {name}",
                                       font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                       text_color=status_color)
            status_label.pack(anchor="w")
            
            # Output/Error
            if output:
                out_text = output[:300].strip()
                out_label = ctk.CTkLabel(result_frame, text=out_text,
                                        font=ctk.CTkFont(family="Consolas", size=9),
                                        text_color=COLORS['text_secondary'],
                                        justify="left", wraplength=600)
                out_label.pack(anchor="w", padx=12, pady=(0, 4))
            
            if error:
                err_text = error[:300].strip()
                err_label = ctk.CTkLabel(result_frame, text=err_text,
                                        font=ctk.CTkFont(family="Consolas", size=9),
                                        text_color=COLORS['error'],
                                        justify="left", wraplength=600)
                err_label.pack(anchor="w", padx=12, pady=(0, 10))
        
        # Summary at top
        summary_frame = ctk.CTkFrame(self.results_frame, fg_color='transparent')
        summary_frame.pack(fill="x", padx=15, pady=(0, 15), anchor="w")
        
        summary_text = f"Results: {passed} passed, {failed} failed / {len(selected)} total"
        summary_color = COLORS['success'] if failed == 0 else COLORS['warning']
        
        summary_label = ctk.CTkLabel(summary_frame, text=summary_text,
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                    text_color=summary_color)
        summary_label.pack(anchor="w")
        
        # Log to parent
        self.parent._log(f"System Test Results: {passed} passed, {failed} failed")


def main():
    try:
        logging.info("=== Haven Control Room Starting ===")
        logging.info(f"Python: {sys.version}")
        logging.info(f"Platform: {sys.platform}")
        logging.info(f"Working directory: {Path.cwd()}")

        # Support dispatching alternate entries when frozen
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--entry', choices=['control', 'system', 'map'])
        parser.add_argument('--no-open', action='store_true')
        args, unknown = parser.parse_known_args()

        entry = args.entry or 'control'
        logging.info(f"Entry point: {entry}")

        if entry == 'system':
            # Run the System Entry UI as a separate process entrypoint
            # Use runpy to invoke module as __main__
            logging.info("Launching System Entry Wizard module...")
            runpy.run_module('system_entry_wizard', run_name='__main__')
            return
        if entry == 'map':
            # Forward args to map generator
            logging.info("Launching Map Generator module...")
            sys.argv = ['Beta_VH_Map.py'] + (['--no-open'] if args.no_open else [])
            runpy.run_module('Beta_VH_Map', run_name='__main__')
            return

        # Default: Control Room UI
        logging.info("Initializing Control Room UI...")
        app = ControlRoom()
        logging.info("Starting main event loop...")
        app.mainloop()
        logging.info("Control Room closed normally.")

    except Exception as e:
        logging.error(f"FATAL ERROR in main(): {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        # Try to show error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Control Room Error",
                                f"Failed to start Control Room:\n\n{e}\n\nCheck logs/error_logs/ for details.")
            root.destroy()
        except:
            pass
        sys.exit(1)


if __name__ == '__main__':
    main()
