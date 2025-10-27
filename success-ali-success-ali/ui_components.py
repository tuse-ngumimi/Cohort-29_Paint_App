"""
UI Components Module
Contributor: Person 1

This module handles all UI layout, toolbar creation, and widget management.
Responsibilities:
- Build toolbar with tool buttons
- Create color picker and quick color buttons
- Brush size slider and preview
- Fill mode radio buttons
- Action buttons (Undo/Redo/Clear/Save)
- Status bar
- Canvas creation
"""

import tkinter as tk
from tkinter import colorchooser

CANVAS_BG = "white"


class UIComponents:
    def __init__(self, app):
        self.app = app

    def build_ui(self):
        """Build the complete UI layout"""
        self._build_toolbar()
        self._build_canvas()
        self._build_status_bar()

    def _build_toolbar(self):
        """Create top toolbar with all controls"""
        toolbar = tk.Frame(self.app.root, relief=tk.RAISED, bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self._build_tool_buttons(toolbar)
        self._build_color_picker(toolbar)
        self._build_brush_controls(toolbar)
        self._build_fill_mode(toolbar)
        self._build_action_buttons(toolbar)

    def _build_tool_buttons(self, parent):
        """Create tool selection buttons"""
        tools_frame = tk.Frame(parent)
        tools_frame.pack(side=tk.LEFT, padx=6)
        
        tk.Button(tools_frame, text="✏ Freehand", width=10, 
                 command=lambda: self.select_tool("freehand")).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="📏 Line", width=10, 
                 command=lambda: self.select_tool("line")).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="▭ Rectangle", width=10, 
                 command=lambda: self.select_tool("rectangle")).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="⭕ Oval", width=10, 
                 command=lambda: self.select_tool("oval")).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="🩹 Eraser", width=8, 
                 command=lambda: self.select_tool("eraser")).pack(side=tk.LEFT, padx=8)

    def _build_color_picker(self, parent):
        """Create color picker and quick color buttons"""
        color_frame = tk.Frame(parent)
        color_frame.pack(side=tk.LEFT, padx=6)
        
        tk.Button(color_frame, text="Pick Color", command=self.choose_color).pack(side=tk.LEFT)
        
        quick_colors = ["#000000", "#FF0000", "#0000FF", "#00AA00", 
                       "#FFD700", "#FFA500", "#800080", "#FFC0CB"]
        for c in quick_colors:
            btn = tk.Button(color_frame, bg=c, width=2, 
                          command=lambda col=c: self.set_color(col))
            btn.pack(side=tk.LEFT, padx=2)

    def _build_brush_controls(self, parent):
        """Create brush size slider and preview"""
        size_frame = tk.Frame(parent)
        size_frame.pack(side=tk.LEFT, padx=6)
        
        tk.Label(size_frame, text="Brush").pack(side=tk.LEFT)
        
        self.app.size_var = tk.IntVar(value=self.app.brush_size)
        size_slider = tk.Scale(size_frame, from_=1, to=40, orient=tk.HORIZONTAL,
                              variable=self.app.size_var, command=self.on_brush_change, 
                              length=140)
        size_slider.pack(side=tk.LEFT)
        
        self.app.preview_canvas = tk.Canvas(size_frame, width=40, height=40, 
                                           bg="white", bd=1, relief=tk.SUNKEN)
        self.app.preview_canvas.pack(side=tk.LEFT, padx=6)
        self.draw_brush_preview()

    def _build_fill_mode(self, parent):
        """Create fill mode radio buttons"""
        fill_frame = tk.Frame(parent)
        fill_frame.pack(side=tk.LEFT, padx=6)
        
        tk.Label(fill_frame, text="Fill:").pack(side=tk.LEFT)
        
        self.app.fill_var = tk.StringVar(value=self.app.fill_mode)
        tk.Radiobutton(fill_frame, text="Outline", variable=self.app.fill_var, 
                      value="outline", command=self.on_fill_change).pack(side=tk.LEFT)
        tk.Radiobutton(fill_frame, text="Filled", variable=self.app.fill_var, 
                      value="filled", command=self.on_fill_change).pack(side=tk.LEFT)
        tk.Radiobutton(fill_frame, text="Both", variable=self.app.fill_var, 
                      value="both", command=self.on_fill_change).pack(side=tk.LEFT)

    def _build_action_buttons(self, parent):
        """Create action buttons (Undo/Redo/Clear/Save)"""
        action_frame = tk.Frame(parent)
        action_frame.pack(side=tk.RIGHT, padx=6)
        
        self.app.undo_btn = tk.Button(action_frame, text="↶ Undo", 
                                      command=self.app.file_ops.undo, 
                                      state=tk.DISABLED, width=8)
        self.app.undo_btn.pack(side=tk.LEFT, padx=3)
        
        self.app.redo_btn = tk.Button(action_frame, text="↷ Redo", 
                                      command=self.app.file_ops.redo, 
                                      state=tk.DISABLED, width=8)
        self.app.redo_btn.pack(side=tk.LEFT, padx=3)
        
        tk.Button(action_frame, text="Clear", command=self.app.file_ops.clear_canvas, 
                 width=8).pack(side=tk.LEFT, padx=3)
        tk.Button(action_frame, text="Save PNG", command=self.app.file_ops.save_as_png, 
                 width=10).pack(side=tk.LEFT, padx=3)

    def _build_canvas(self):
        """Create main drawing canvas"""
        self.app.canvas = tk.Canvas(self.app.root, bg=CANVAS_BG, cursor="cross", 
                                   highlightthickness=0)
        self.app.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def _build_status_bar(self):
        """Create bottom status bar"""
        status = tk.Frame(self.app.root, bd=1, relief=tk.SUNKEN)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.app.status_label = tk.Label(status, 
                                         text="Tool: freehand  |  Color: #000000  |  Brush: 4px", 
                                         anchor=tk.W)
        self.app.status_label.pack(side=tk.LEFT)

    # UI Helper Methods
    def select_tool(self, tool_name: str):
        """Change current drawing tool"""
        self.app.current_tool = tool_name
        self.update_status()

    def choose_color(self):
        """Open color chooser dialog"""
        c = colorchooser.askcolor(color=self.app.current_color)
        if c and c[1]:
            self.set_color(c[1])

    def set_color(self, color_hex: str):
        """Set current drawing color"""
        self.app.current_color = color_hex
        self.draw_brush_preview()
        self.update_status()

    def on_brush_change(self, val):
        """Handle brush size slider change"""
        try:
            self.app.brush_size = int(val)
        except Exception:
            self.app.brush_size = self.app.size_var.get()
        self.draw_brush_preview()
        self.update_status()

    def on_fill_change(self):
        """Handle fill mode change"""
        self.app.fill_mode = self.app.fill_var.get()

    def draw_brush_preview(self):
        """Draw brush size/color preview"""
        self.app.preview_canvas.delete("all")
        r = max(2, self.app.brush_size // 2)
        cx, cy = 20, 20
        self.app.preview_canvas.create_rectangle(0, 0, 40, 40, fill="white", outline="")
        self.app.preview_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, 
                                          fill=self.app.current_color, outline="black")

    def update_status(self, extra: str = ""):
        """Update status bar text"""
        color_text = self.app.current_color
        self.app.status_label.config(
            text=f"Tool: {self.app.current_tool}  |  Color: {color_text}  |  Brush: {self.app.brush_size}px {extra}"
        )
