"""
Test Manager Window - Centralized test script management and execution
"""

import customtkinter as ctk
from pathlib import Path
import subprocess
import threading
import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
import sys

# Add project root to path
_proj_root = Path(__file__).parent.parent
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

from src.common.paths import project_root

# Colors matching Control Room theme
COLORS = {
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
    'glass': '#1a2342'
}


class TestManagerWindow(ctk.CTkToplevel):
    """Main Test Manager window"""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Haven Test Manager 🧪")
        self.geometry("1400x900")
        self.configure(fg_color=COLORS['bg_dark'])

        # Test results database
        self.results_db_path = project_root() / "Program-tests" / "test_results.json"
        self.results_db = self._load_results_db()

        # Current running test
        self.running_test = None
        self.test_process = None

        self._create_ui()
        self._load_tests()

    def _load_results_db(self):
        """Load test results database"""
        if self.results_db_path.exists():
            try:
                with open(self.results_db_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_results_db(self):
        """Save test results database"""
        try:
            self.results_db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.results_db_path, 'w') as f:
                json.dump(self.results_db, f, indent=2)
        except Exception as e:
            print(f"Error saving results: {e}")

    def _create_ui(self):
        """Create the UI layout"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_card'])
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🧪 Haven Test Manager",
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS['accent_cyan']
        )
        title_label.pack(side="left", padx=20, pady=15)

        # Add test button
        add_btn = ctk.CTkButton(
            title_frame,
            text="➕ Add New Test",
            command=self._add_test,
            fg_color=COLORS['accent_purple'],
            hover_color=COLORS['accent_pink'],
            height=40,
            font=("Segoe UI", 14, "bold")
        )
        add_btn.pack(side="right", padx=20, pady=15)

        # Export button
        export_btn = ctk.CTkButton(
            title_frame,
            text="📤 Export Results",
            command=self._export_results,
            fg_color=COLORS['glass'],
            hover_color=COLORS['accent_purple'],
            height=40,
            font=("Segoe UI", 14)
        )
        export_btn.pack(side="right", padx=(0, 10), pady=15)

        # Content area (split pane)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Left panel - Test tree
        left_panel = ctk.CTkFrame(content_frame, fg_color=COLORS['bg_card'], width=450)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_panel.pack_propagate(False)

        tree_title = ctk.CTkLabel(
            left_panel,
            text="📋 Test Categories",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS['accent_cyan']
        )
        tree_title.pack(pady=(15, 10), padx=15, anchor="w")

        # Scrollable frame for tests
        self.test_scroll = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=COLORS['bg_dark'],
            scrollbar_button_color=COLORS['accent_cyan'],
            scrollbar_button_hover_color=COLORS['accent_purple']
        )
        self.test_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Right panel - Test details and output
        right_panel = ctk.CTkFrame(content_frame, fg_color=COLORS['bg_card'])
        right_panel.pack(side="right", fill="both", expand=True)

        # Test info section
        info_frame = ctk.CTkFrame(right_panel, fg_color=COLORS['glass'])
        info_frame.pack(fill="x", padx=15, pady=15)

        self.test_name_label = ctk.CTkLabel(
            info_frame,
            text="No test selected",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS['text_primary']
        )
        self.test_name_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.test_desc_label = ctk.CTkLabel(
            info_frame,
            text="Select a test from the left panel to view details",
            font=("Segoe UI", 12),
            text_color=COLORS['text_secondary'],
            wraplength=800,
            justify="left"
        )
        self.test_desc_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Test metadata
        metadata_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        metadata_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.status_label = ctk.CTkLabel(
            metadata_frame,
            text="Status: Unknown",
            font=("Segoe UI", 11),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(side="left", padx=(0, 20))

        self.runtime_label = ctk.CTkLabel(
            metadata_frame,
            text="Last Runtime: N/A",
            font=("Segoe UI", 11),
            text_color=COLORS['text_secondary']
        )
        self.runtime_label.pack(side="left", padx=(0, 20))

        self.modified_label = ctk.CTkLabel(
            metadata_frame,
            text="Modified: N/A",
            font=("Segoe UI", 11),
            text_color=COLORS['text_secondary']
        )
        self.modified_label.pack(side="left")

        # Action buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.run_btn = ctk.CTkButton(
            btn_frame,
            text="▶️ Run Test",
            command=self._run_selected_test,
            fg_color=COLORS['success'],
            hover_color="#00cc66",
            height=45,
            font=("Segoe UI", 14, "bold"),
            state="disabled"
        )
        self.run_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Edit Test",
            command=self._edit_selected_test,
            fg_color=COLORS['accent_purple'],
            hover_color=COLORS['accent_pink'],
            height=45,
            font=("Segoe UI", 14, "bold"),
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.view_btn = ctk.CTkButton(
            btn_frame,
            text="📊 View Results History",
            command=self._view_results_history,
            fg_color=COLORS['glass'],
            hover_color=COLORS['accent_cyan'],
            height=45,
            font=("Segoe UI", 14, "bold"),
            state="disabled"
        )
        self.view_btn.pack(side="left", fill="x", expand=True)

        # Progress bar
        self.progress_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            progress_color=COLORS['accent_cyan'],
            height=20
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready",
            font=("Segoe UI", 11),
            text_color=COLORS['text_secondary']
        )
        self.progress_label.pack(pady=(5, 0))

        # Output area
        output_label = ctk.CTkLabel(
            right_panel,
            text="📝 Test Output",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS['accent_cyan']
        )
        output_label.pack(anchor="w", padx=15, pady=(5, 5))

        self.output_text = ctk.CTkTextbox(
            right_panel,
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text_primary'],
            font=("Consolas", 11),
            wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Clear output button
        clear_btn = ctk.CTkButton(
            right_panel,
            text="🗑️ Clear Output",
            command=lambda: self.output_text.delete("1.0", "end"),
            fg_color=COLORS['glass'],
            hover_color=COLORS['error'],
            height=35,
            font=("Segoe UI", 12)
        )
        clear_btn.pack(padx=15, pady=(0, 15))

    def _load_tests(self):
        """Load all test files from Program-tests folder"""
        program_tests_dir = project_root() / "Program-tests"

        if not program_tests_dir.exists():
            messagebox.showerror("Error", "Program-tests folder not found!")
            return

        # Clear existing
        for widget in self.test_scroll.winfo_children():
            widget.destroy()

        # Load test structure
        categories = {}
        for category_dir in sorted(program_tests_dir.iterdir()):
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue

            category_name = category_dir.name
            categories[category_name] = {}

            # Get subcategories
            for subcat_dir in sorted(category_dir.iterdir()):
                if not subcat_dir.is_dir() or subcat_dir.name.startswith('.'):
                    continue

                subcat_name = subcat_dir.name
                test_files = list(subcat_dir.glob("*.py"))

                if test_files:
                    categories[category_name][subcat_name] = test_files

        # Create expandable category sections
        for category, subcats in categories.items():
            if not subcats:  # Skip empty categories
                continue

            # Category header
            cat_frame = ctk.CTkFrame(self.test_scroll, fg_color=COLORS['bg_card'])
            cat_frame.pack(fill="x", pady=(0, 5))

            cat_btn = ctk.CTkButton(
                cat_frame,
                text=f"📁 {category}",
                command=lambda c=category: self._toggle_category(c),
                fg_color=COLORS['accent_purple'],
                hover_color=COLORS['accent_pink'],
                anchor="w",
                font=("Segoe UI", 14, "bold"),
                height=40
            )
            cat_btn.pack(fill="x", padx=5, pady=5)

            # Subcategories container (collapsible)
            subcat_container = ctk.CTkFrame(cat_frame, fg_color=COLORS['glass'])
            subcat_container.pack(fill="x", padx=10, pady=(0, 5))
            subcat_container.category_name = category
            subcat_container.is_visible = True

            for subcat, files in subcats.items():
                # Subcategory header
                subcat_label = ctk.CTkLabel(
                    subcat_container,
                    text=f"  📂 {subcat}",
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['accent_cyan'],
                    anchor="w"
                )
                subcat_label.pack(fill="x", padx=10, pady=(10, 5))

                # Test files
                for test_file in files:
                    self._create_test_button(subcat_container, test_file, category, subcat)

    def _toggle_category(self, category_name):
        """Toggle category visibility"""
        for widget in self.test_scroll.winfo_children():
            for child in widget.winfo_children():
                if hasattr(child, 'category_name') and child.category_name == category_name:
                    if child.is_visible:
                        child.pack_forget()
                        child.is_visible = False
                    else:
                        child.pack(fill="x", padx=10, pady=(0, 5))
                        child.is_visible = True

    def _create_test_button(self, parent, test_file, category, subcategory):
        """Create button for a test file"""
        test_btn = ctk.CTkButton(
            parent,
            text=f"    🧪 {test_file.stem}",
            command=lambda: self._select_test(test_file, category, subcategory),
            fg_color=COLORS['bg_dark'],
            hover_color=COLORS['glass'],
            anchor="w",
            font=("Segoe UI", 11),
            height=35
        )
        test_btn.pack(fill="x", padx=15, pady=2)

    def _select_test(self, test_file, category, subcategory):
        """Select a test and show its details"""
        self.selected_test = test_file
        self.selected_category = category
        self.selected_subcategory = subcategory

        # Update test info
        self.test_name_label.configure(text=test_file.stem)

        # Get description from docstring
        description = self._get_test_description(test_file)
        self.test_desc_label.configure(text=description)

        # Update metadata
        modified_time = datetime.fromtimestamp(test_file.stat().st_mtime)
        self.modified_label.configure(text=f"Modified: {modified_time.strftime('%Y-%m-%d %H:%M')}")

        # Get last run info
        test_key = str(test_file.relative_to(project_root()))
        if test_key in self.results_db:
            result = self.results_db[test_key]
            status = result.get('status', 'Unknown')
            runtime = result.get('runtime', 'N/A')

            status_color = COLORS['success'] if status == 'PASS' else COLORS['error'] if status == 'FAIL' else COLORS['warning']
            self.status_label.configure(text=f"Status: {status}", text_color=status_color)
            self.runtime_label.configure(text=f"Last Runtime: {runtime:.2f}s" if isinstance(runtime, (int, float)) else f"Last Runtime: {runtime}")
        else:
            self.status_label.configure(text="Status: Never run", text_color=COLORS['text_secondary'])
            self.runtime_label.configure(text="Last Runtime: N/A")

        # Enable buttons
        self.run_btn.configure(state="normal")
        self.edit_btn.configure(state="normal")
        self.view_btn.configure(state="normal")

    def _get_test_description(self, test_file):
        """Extract description from test file docstring"""
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                # Look for module docstring
                if '"""' in content:
                    start = content.index('"""') + 3
                    end = content.index('"""', start)
                    docstring = content[start:end].strip()
                    # Return first line
                    return docstring.split('\n')[0][:150]
        except:
            pass
        return "No description available"

    def _run_selected_test(self):
        """Run the selected test"""
        if not hasattr(self, 'selected_test'):
            return

        # Disable run button
        self.run_btn.configure(state="disabled", text="⏳ Running...")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", f"Running {self.selected_test.name}...\n")
        self.output_text.insert("end", f"{'='*60}\n\n")

        # Start progress animation
        self.progress_bar.set(0)
        self.progress_label.configure(text="Test in progress...")
        self._animate_progress()

        # Run test in thread
        threading.Thread(target=self._execute_test, daemon=True).start()

    def _animate_progress(self):
        """Animate progress bar"""
        if self.running_test:
            current = self.progress_bar.get()
            if current < 0.95:
                self.progress_bar.set(current + 0.01)
            self.after(100, self._animate_progress)

    def _execute_test(self):
        """Execute test in subprocess"""
        test_file = self.selected_test
        self.running_test = True

        start_time = datetime.now()

        try:
            # Run test
            result = subprocess.run(
                ["python3", str(test_file)],
                capture_output=True,
                text=True,
                cwd=str(project_root()),
                timeout=300  # 5 minute timeout
            )

            end_time = datetime.now()
            runtime = (end_time - start_time).total_seconds()

            # Update UI
            self.after(0, lambda: self._display_test_result(result, runtime))

        except subprocess.TimeoutExpired:
            self.after(0, lambda: self._display_timeout())
        except Exception as e:
            self.after(0, lambda: self._display_error(str(e)))
        finally:
            self.running_test = False

    def _display_test_result(self, result, runtime):
        """Display test results"""
        # Clear and show output
        self.output_text.delete("1.0", "end")

        # Status
        status = "PASS" if result.returncode == 0 else "FAIL"
        status_color = COLORS['success'] if status == "PASS" else COLORS['error']

        header = f"{'='*60}\n"
        header += f"TEST: {self.selected_test.name}\n"
        header += f"STATUS: {status}\n"
        header += f"RUNTIME: {runtime:.2f}s\n"
        header += f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"{'='*60}\n\n"

        self.output_text.insert("1.0", header)

        # Output
        if result.stdout:
            self.output_text.insert("end", "STDOUT:\n")
            self.output_text.insert("end", result.stdout)
            self.output_text.insert("end", "\n\n")

        if result.stderr:
            self.output_text.insert("end", "STDERR:\n")
            self.output_text.insert("end", result.stderr)
            self.output_text.insert("end", "\n")

        # Update progress
        self.progress_bar.set(1.0)
        self.progress_label.configure(text=f"✓ Complete - {status}")

        # Save result to database
        test_key = str(self.selected_test.relative_to(project_root()))
        self.results_db[test_key] = {
            'status': status,
            'runtime': runtime,
            'timestamp': datetime.now().isoformat(),
            'returncode': result.returncode
        }
        self._save_results_db()

        # Re-enable button
        self.run_btn.configure(state="normal", text="▶️ Run Test")

        # Update status display
        self.status_label.configure(text=f"Status: {status}", text_color=status_color)
        self.runtime_label.configure(text=f"Last Runtime: {runtime:.2f}s")

    def _display_timeout(self):
        """Display timeout message"""
        self.output_text.insert("end", "\n❌ TEST TIMEOUT\n")
        self.output_text.insert("end", "Test exceeded 5 minute timeout limit\n")
        self.progress_bar.set(0)
        self.progress_label.configure(text="⚠️ Timeout")
        self.run_btn.configure(state="normal", text="▶️ Run Test")

    def _display_error(self, error_msg):
        """Display error message"""
        self.output_text.insert("end", f"\n❌ ERROR\n{error_msg}\n")
        self.progress_bar.set(0)
        self.progress_label.configure(text="❌ Error")
        self.run_btn.configure(state="normal", text="▶️ Run Test")

    def _edit_selected_test(self):
        """Open selected test in default editor"""
        if not hasattr(self, 'selected_test'):
            return

        try:
            if sys.platform == 'win32':
                os.startfile(self.selected_test)
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(self.selected_test)])
            else:
                subprocess.run(['xdg-open', str(self.selected_test)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open test file:\n{e}")

    def _view_results_history(self):
        """View test results history"""
        if not hasattr(self, 'selected_test'):
            return

        test_key = str(self.selected_test.relative_to(project_root()))
        if test_key not in self.results_db:
            messagebox.showinfo("No History", "This test has not been run yet.")
            return

        result = self.results_db[test_key]
        history_text = "Test Results History\n"
        history_text += "=" * 50 + "\n\n"
        history_text += f"Test: {self.selected_test.name}\n"
        history_text += f"Status: {result.get('status', 'Unknown')}\n"
        history_text += f"Runtime: {result.get('runtime', 'N/A')}s\n"
        history_text += f"Last Run: {result.get('timestamp', 'N/A')}\n"
        history_text += f"Return Code: {result.get('returncode', 'N/A')}\n"

        messagebox.showinfo("Test History", history_text)

    def _add_test(self):
        """Add a new test via file browser"""
        file_path = filedialog.askopenfilename(
            title="Select Test Script",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        # Ask for category and subcategory
        category = self._prompt_category()
        if not category:
            return

        subcategory = self._prompt_subcategory(category)
        if not subcategory:
            return

        # Copy file to Program-tests
        source = Path(file_path)
        target_dir = project_root() / "Program-tests" / category / subcategory
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name

        try:
            import shutil
            shutil.copy2(source, target)
            messagebox.showinfo("Success", f"Test added to {category}/{subcategory}")
            self._load_tests()  # Refresh
        except Exception as e:
            messagebox.showerror("Error", f"Could not add test:\n{e}")

    def _prompt_category(self):
        """Prompt user to select or create category"""
        program_tests_dir = project_root() / "Program-tests"
        categories = [d.name for d in program_tests_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]

        # Simple dialog
        dialog = ctk.CTkInputDialog(
            text=f"Enter category name:\n(Existing: {', '.join(categories)})",
            title="Select Category"
        )
        return dialog.get_input()

    def _prompt_subcategory(self, category):
        """Prompt user to select or create subcategory"""
        cat_dir = project_root() / "Program-tests" / category
        if cat_dir.exists():
            subcats = [d.name for d in cat_dir.iterdir() if d.is_dir()]
            subcats_text = f"(Existing: {', '.join(subcats)})" if subcats else ""
        else:
            subcats_text = ""

        dialog = ctk.CTkInputDialog(
            text=f"Enter subcategory name:\n{subcats_text}",
            title="Select Subcategory"
        )
        return dialog.get_input()

    def _export_results(self):
        """Export test results to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Test Results",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'total_tests': len(self.results_db),
                'results': self.results_db
            }

            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export results:\n{e}")


# Test the window
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.withdraw()  # Hide root window
    test_manager = TestManagerWindow(app)
    test_manager.mainloop()
