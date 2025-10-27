"""
File Operations Module
Contributor: Person 3

This module handles file operations and history management.
Responsibilities:
- Undo/Redo functionality
- Clear canvas
- Save canvas as PNG
- History stack management
- Button state updates
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageGrab


class FileOperations:
    def __init__(self, app):
        self.app = app

    def undo(self):
        """Undo last drawing action"""
        if not self.app.history_stack:
            return
        
        last_id = self.app.history_stack.pop()
        try:
            self.app.canvas.delete(last_id)
            self.app.redo_stack.append(last_id)
            self.update_buttons()
        except Exception:
            pass

    def redo(self):
        """Redo last undone action"""
        if not self.app.redo_stack:
            return
        
        try:
            item = self.app.redo_stack.pop()
            # Note: Canvas does not allow recreating deleted items by ID.
            # A full redo implementation would require storing operation data
            # (operation type, coordinates, colors, etc.) instead of just IDs.
            # For now, we show a message about the limitation.
            messagebox.showinfo("Redo", 
                              "Redo is not supported after full delete (session-limited).")
            self.update_buttons()
        except Exception:
            pass

    def clear_canvas(self):
        """Clear entire canvas and reset history"""
        self.app.canvas.delete("all")
        self.app.history_stack.clear()
        self.app.redo_stack.clear()
        self.update_buttons()

    def update_buttons(self):
        """Update undo/redo button states based on history stacks"""
        # Undo button
        if self.app.history_stack:
            self.app.undo_btn.config(state=tk.NORMAL)
        else:
            self.app.undo_btn.config(state=tk.DISABLED)

        # Redo button
        if self.app.redo_stack:
            self.app.redo_btn.config(state=tk.NORMAL)
        else:
            self.app.redo_btn.config(state=tk.DISABLED)

    def save_as_png(self):
        """Save canvas as PNG image file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Get canvas position relative to screen
            x = self.app.canvas.winfo_rootx()
            y = self.app.canvas.winfo_rooty()
            x1 = x + self.app.canvas.winfo_width()
            y1 = y + self.app.canvas.winfo_height()
            
            # Capture and crop screenshot of canvas area
            img = ImageGrab.grab().crop((x, y, x1, y1))
            img.save(file_path)
            
            messagebox.showinfo("Saved", f"Canvas saved to\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save image: {e}")

