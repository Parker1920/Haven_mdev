"""
Backup Management UI Dialog

Provides a CustomTkinter dialog for viewing and managing data backups.
Displays backup history with timestamps, sizes, and descriptions.
Allows restoration from any backup point and manual backup creation.

Features:
    - List all backups with metadata
    - Create manual backups with descriptions
    - Restore from any backup point
    - Automatic backup on data modifications
    - Backup verification and integrity checking
    - Orphaned file cleanup

Usage:
    from src.common.backup_ui import BackupDialog
    
    dialog = BackupDialog(parent_window)
    # Dialog is modal and handles all interactions
"""

import customtkinter as ctk
from tkinter import messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

from common.backup_manager import get_backup_manager, BackupManager
from common.theme import COLORS


class BackupDialog(ctk.CTkToplevel):
    """Modal dialog for managing data backups."""
    
    def __init__(self, parent: ctk.CTk, on_restore: Optional[Callable] = None):
        """
        Initialize backup management dialog.
        
        Args:
            parent: Parent window
            on_restore: Callback function called after successful restore
        """
        super().__init__(parent)
        self.title("Data Backup Management")
        self.geometry("700x600")
        self.configure(fg_color=COLORS['bg_card'])
        self.parent = parent
        self.on_restore = on_restore
        self.resizable(True, True)
        
        self.backup_manager = get_backup_manager()
        
        try:
            self._build_ui()
            self._load_backups()
            self.grab_set()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize backup dialog: {e}")
            self.destroy()
    
    def _build_ui(self):
        """Build the dialog UI."""
        # Header
        header = ctk.CTkLabel(
            self,
            text="Data Backup Management",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        )
        header.pack(pady=(15, 5), padx=15)
        
        info = ctk.CTkLabel(
            self,
            text="View and restore previous versions of your data",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        info.pack(pady=(0, 15), padx=15)
        
        # Backup list frame
        list_frame = ctk.CTkFrame(self, fg_color='transparent')
        list_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Backups label
        backups_label = ctk.CTkLabel(
            list_frame,
            text="Available Backups",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        )
        backups_label.pack(anchor='w', pady=(0, 8))
        
        # Scrollable backups list
        self.scroll_frame = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=COLORS['glass'],
            height=250
        )
        self.scroll_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Placeholder for backup items
        self.backup_items = []
        
        # Details frame (hidden by default)
        self.details_frame = ctk.CTkFrame(list_frame, fg_color=COLORS['bg_dark'], corner_radius=6)
        self.details_frame.pack(fill='x', pady=10, padx=8)
        
        details_label = ctk.CTkLabel(
            self.details_frame,
            text="Backup Details",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS['text_primary']
        )
        details_label.pack(anchor='w', pady=(10, 5), padx=10)
        
        self.details_text = scrolledtext.ScrolledText(
            self.details_frame,
            height=4,
            width=50,
            bg=COLORS['bg_dark'],
            fg=COLORS['text_primary'],
            font=("Courier", 9)
        )
        self.details_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.details_text.config(state='disabled')
        
        # Button frame
        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        # Create backup button
        create_btn = ctk.CTkButton(
            btn_frame,
            text="📦 Create Backup",
            command=self._create_backup,
            fg_color=COLORS['accent_cyan'],
            text_color=COLORS['bg_dark'],
            width=100
        )
        create_btn.pack(side='left', padx=5)
        
        # Verify button
        verify_btn = ctk.CTkButton(
            btn_frame,
            text="✓ Verify All",
            command=self._verify_backups,
            fg_color=COLORS['success'],
            text_color=COLORS['bg_dark'],
            width=100
        )
        verify_btn.pack(side='left', padx=5)
        
        # Restore button
        self.restore_btn = ctk.CTkButton(
            btn_frame,
            text="↩️ Restore",
            command=self._restore_selected,
            fg_color=COLORS['warning'],
            text_color=COLORS['bg_dark'],
            width=100,
            state='disabled'
        )
        self.restore_btn.pack(side='left', padx=5)
        
        # Close button
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            command=self.destroy,
            fg_color=COLORS['glass'],
            text_color=COLORS['text_primary'],
            width=100
        )
        close_btn.pack(side='right', padx=5)
        
        self.selected_backup = None
    
    def _load_backups(self):
        """Load and display available backups."""
        # Clear existing items
        for item in self.backup_items:
            item.destroy()
        self.backup_items.clear()
        
        # Get backups
        backups = self.backup_manager.list_backups()
        
        if not backups:
            no_backups_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No backups available yet. Click 'Create Backup' to create one.",
                text_color=COLORS['text_secondary']
            )
            no_backups_label.pack(pady=20)
            self.backup_items.append(no_backups_label)
            return
        
        # Display backups
        for backup in backups:
            self._create_backup_item(backup)
    
    def _create_backup_item(self, backup: dict):
        """Create UI item for a single backup."""
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(backup['timestamp'])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = backup['timestamp']
        
        # Size formatting
        size_mb = backup['file_size'] / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{backup['file_size'] / 1024:.2f} KB"
        
        # Item frame
        item_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS['bg_dark'],
            corner_radius=6
        )
        item_frame.pack(fill='x', pady=5, padx=5)
        
        # Content frame (clickable)
        content_frame = ctk.CTkFrame(item_frame, fg_color='transparent')
        content_frame.pack(fill='x', padx=10, pady=8)
        
        # Make content frame clickable
        backup_id = backup['backup_id']
        content_frame.bind(
            '<Button-1>',
            lambda e: self._select_backup(backup_id, backup, item_frame)
        )
        
        # Header with timestamp and hash
        header_frame = ctk.CTkFrame(content_frame, fg_color='transparent')
        header_frame.pack(fill='x')
        
        time_label = ctk.CTkLabel(
            header_frame,
            text=f"📅 {time_str}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS['accent_cyan']
        )
        time_label.pack(side='left', anchor='w')
        time_label.bind('<Button-1>', lambda e: self._select_backup(backup_id, backup, item_frame))
        
        hash_label = ctk.CTkLabel(
            header_frame,
            text=f"Hash: {backup['file_hash']}",
            font=ctk.CTkFont(family="Courier", size=9),
            text_color=COLORS['text_secondary']
        )
        hash_label.pack(side='right', anchor='e')
        hash_label.bind('<Button-1>', lambda e: self._select_backup(backup_id, backup, item_frame))
        
        # Description
        if backup.get('description'):
            desc_label = ctk.CTkLabel(
                content_frame,
                text=f"📝 {backup['description']}",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=COLORS['text_primary']
            )
            desc_label.pack(fill='x', pady=(4, 0), anchor='w')
            desc_label.bind('<Button-1>', lambda e: self._select_backup(backup_id, backup, item_frame))
        
        # Info footer
        info_label = ctk.CTkLabel(
            content_frame,
            text=f"Size: {size_str} | ID: {backup_id}",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=COLORS['text_secondary']
        )
        info_label.pack(fill='x', pady=(4, 0), anchor='w')
        info_label.bind('<Button-1>', lambda e: self._select_backup(backup_id, backup, item_frame))
        
        self.backup_items.append(item_frame)
    
    def _select_backup(self, backup_id: str, backup: dict, item_frame: ctk.CTkFrame):
        """Select a backup and show details."""
        self.selected_backup = backup
        
        # Highlight selected item
        for item in self.backup_items:
            item.configure(fg_color=COLORS['bg_dark'])
        item_frame.configure(fg_color=COLORS['accent_cyan'])
        
        # Show details
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        
        details = f"""Backup ID: {backup_id}
Timestamp: {backup['timestamp']}
Hash: {backup['file_hash']}
Size: {backup['file_size']} bytes ({backup['file_size'] / (1024 * 1024):.2f} MB)
Status: {backup['status']}
Description: {backup.get('description', '(none)')}"""
        
        self.details_text.insert('1.0', details)
        self.details_text.config(state='disabled')
        
        # Enable restore button
        self.restore_btn.configure(state='normal')
    
    def _create_backup(self):
        """Create a new backup with description."""
        # Create input dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Backup")
        dialog.geometry("400x150")
        dialog.configure(fg_color=COLORS['bg_card'])
        dialog.grab_set()
        
        label = ctk.CTkLabel(
            dialog,
            text="Backup Description (optional):",
            text_color=COLORS['text_primary']
        )
        label.pack(pady=10, padx=15)
        
        entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g., Before system deletion",
            fg_color=COLORS['glass'],
            text_color=COLORS['text_primary']
        )
        entry.pack(pady=5, padx=15, fill='x')
        
        def save_backup():
            description = entry.get()
            backup_id = self.backup_manager.create_backup(description)
            if backup_id:
                messagebox.showinfo("Success", f"Backup created: {backup_id}")
                self._load_backups()
            else:
                messagebox.showerror("Error", "Failed to create backup")
            dialog.destroy()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color='transparent')
        btn_frame.pack(pady=10)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Create",
            command=save_backup,
            fg_color=COLORS['accent_cyan'],
            text_color=COLORS['bg_dark']
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color=COLORS['glass'],
            text_color=COLORS['text_primary']
        )
        cancel_btn.pack(side='left', padx=5)
    
    def _restore_selected(self):
        """Restore the selected backup."""
        if not self.selected_backup:
            messagebox.showwarning("No Selection", "Please select a backup to restore")
            return
        
        backup_id = self.selected_backup['backup_id']
        
        # Confirm restore
        result = messagebox.askyesno(
            "Confirm Restore",
            f"Restore backup '{backup_id}'?\n\nA backup of current data will be created first.",
            icon=messagebox.WARNING
        )
        
        if not result:
            return
        
        # Perform restore
        if self.backup_manager.restore_backup(backup_id):
            messagebox.showinfo("Success", f"Restored backup: {backup_id}")
            self._load_backups()
            if self.on_restore:
                self.on_restore()
        else:
            messagebox.showerror("Error", "Failed to restore backup")
    
    def _verify_backups(self):
        """Verify integrity of all backups."""
        valid, corrupted = self.backup_manager.verify_backups()
        message = f"Backup Verification Results\n\nValid: {valid}\nCorrupted: {corrupted}"
        
        if corrupted == 0:
            messagebox.showinfo("Verification Complete", message)
        else:
            messagebox.showwarning("Issues Found", message)


class BackupIndicator(ctk.CTkLabel):
    """Simple status indicator showing latest backup info."""
    
    def __init__(self, parent: ctk.CTk, **kwargs):
        """Initialize backup indicator label."""
        super().__init__(parent, **kwargs)
        self.backup_manager = get_backup_manager()
        self._update_status()
    
    def _update_status(self):
        """Update the backup status display."""
        backups = self.backup_manager.list_backups(limit=1)
        
        if backups:
            latest = backups[0]
            timestamp = datetime.fromisoformat(latest['timestamp'])
            time_str = timestamp.strftime("%m/%d %H:%M")
            text = f"📦 Latest backup: {time_str}"
        else:
            text = "📦 No backups"
        
        self.configure(text=text)
