"""
Archived desktop Control Room UI

This file was moved to Archive-Dump/legacy_desktop_20251116/src/control_room.py on 2025-11-16.
The web-first Haven-UI is now the canonical product. See `Haven-UI/README.md` for run instructions.

The full original implementation is preserved in the Archive-Dump folder for reference.
"""

__archived__ = True

def info():
    return "This desktop Control Room UI has been archived. Use Haven-UI web app instead."

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
        self._log("Export functionality has been archived. Use build scripts locally for packaging.")

    def _export_windows(self, output_dir: Path, zip_after: bool = True):
        self._log("Windows export is archived and disabled in the web-first deployment.")

    def _export_macos(self, output_dir: Path):
        self._log("macOS export is archived and disabled in the web-first deployment.")
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

    def open_test_manager(self):
        """Open the Test Manager window."""
        try:
            TestManagerWindow(self)
            self._log("Test Manager opened.")
        except Exception as e:
            self._log(f"Failed to open Test Manager: {e}")
            logging.error(f"Test Manager error: {e}", exc_info=True)

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

    # JSON↔DB sync and export dialogs removed - archived in Archive-Dump
    # Any migration or packaging operations should be performed with the
    # archived scripts in Archive-Dump/ or via the admin API endpoints.


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
    # Enable DPI awareness before creating any windows
    from common.dpi_awareness import set_dpi_awareness
    set_dpi_awareness()

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
