"""
Drawing Tools Module
Contributor: Person 2

This module handles all drawing operations and canvas interactions.
Responsibilities:
- Canvas event handling (mouse press, drag, release, motion)
- Freehand drawing with smoothing
- Shape drawing (line, rectangle, oval)
- Eraser tool
- Preview rendering during drag
- Keyboard shortcuts binding
"""

import tkinter as tk

CANVAS_BG = "white"


class DrawingTools:
    def __init__(self, app):
        self.app = app
        self.preview_id = None

    def bind_events(self):
        """Bind all canvas and keyboard events"""
        self.app.canvas.bind("<Button-1>", self.on_press)
        self.app.canvas.bind("<B1-Motion>", self.on_drag)
        self.app.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.app.canvas.bind("<Motion>", self.on_motion)

        # Keyboard shortcuts
        self.app.root.bind_all("<Control-z>", lambda e: self.app.file_ops.undo())
        self.app.root.bind_all("<Control-y>", lambda e: self.app.file_ops.redo())
        self.app.root.bind_all("<Control-s>", lambda e: self.app.file_ops.save_as_png())

    def on_press(self, event):
        """Handle mouse button press"""
        self.app.start_x, self.app.start_y = event.x, event.y
        
        # Begin new stroke for freehand or eraser
        if self.app.current_tool in ("freehand", "eraser"):
            self.app.current_stroke_points = [(event.x, event.y)]
            self.app.current_stroke_id = None
            # Clear redo on new action
            self.app.redo_stack.clear()
            self.app.file_ops.update_buttons()

    def on_drag(self, event):
        """Handle mouse drag for drawing"""
        if self.app.current_tool in ("freehand", "eraser"):
            self._draw_freehand_stroke(event)
        else:
            self._draw_shape_preview(event)

    def _draw_freehand_stroke(self, event):
        """Draw freehand or eraser stroke with smoothing"""
        self.app.current_stroke_points.append((event.x, event.y))
        
        # Delete previous preview stroke
        if self.app.current_stroke_id:
            try:
                self.app.canvas.delete(self.app.current_stroke_id)
            except Exception:
                pass

        color = CANVAS_BG if self.app.current_tool == "eraser" else self.app.current_color

        if len(self.app.current_stroke_points) >= 3:
            # Draw smoothed line using splines
            flat = [coord for p in self.app.current_stroke_points for coord in p]
            self.app.current_stroke_id = self.app.canvas.create_line(
                *flat, fill=color, width=self.app.brush_size, 
                capstyle=tk.ROUND, smooth=True, splinesteps=36
            )
        else:
            # Draw simple segment for first points
            x1, y1 = self.app.current_stroke_points[-2]
            x2, y2 = self.app.current_stroke_points[-1]
            self.app.current_stroke_id = self.app.canvas.create_line(
                x1, y1, x2, y2, fill=color, width=self.app.brush_size, capstyle=tk.ROUND
            )

    def _draw_shape_preview(self, event):
        """Draw dashed preview for shapes (line, rectangle, oval)"""
        # Remove old preview
        if self.preview_id:
            try:
                self.app.canvas.delete(self.preview_id)
            except Exception:
                pass
            self.preview_id = None

        if self.app.current_tool == "line":
            self.preview_id = self.app.canvas.create_line(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, width=self.app.brush_size, dash=(4, 4)
            )
        elif self.app.current_tool == "rectangle":
            self._draw_rectangle_preview(event)
        elif self.app.current_tool == "oval":
            self._draw_oval_preview(event)

    def _draw_rectangle_preview(self, event):
        """Draw rectangle preview based on fill mode"""
        if self.app.fill_mode == "filled":
            self.preview_id = self.app.canvas.create_rectangle(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline=self.app.current_color, 
                width=self.app.brush_size, dash=(4, 4)
            )
        elif self.app.fill_mode == "both":
            self.preview_id = self.app.canvas.create_rectangle(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline="black", stipple="gray25", 
                width=self.app.brush_size, dash=(4, 4)
            )
        else:  # outline
            self.preview_id = self.app.canvas.create_rectangle(
                self.app.start_x, self.app.start_y, event.x, event.y,
                outline=self.app.current_color, width=self.app.brush_size, dash=(4, 4)
            )

    def _draw_oval_preview(self, event):
        """Draw oval preview based on fill mode"""
        if self.app.fill_mode == "filled":
            self.preview_id = self.app.canvas.create_oval(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline=self.app.current_color, 
                width=self.app.brush_size, dash=(4, 4)
            )
        elif self.app.fill_mode == "both":
            self.preview_id = self.app.canvas.create_oval(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline="black", stipple="gray25", 
                width=self.app.brush_size, dash=(4, 4)
            )
        else:  # outline
            self.preview_id = self.app.canvas.create_oval(
                self.app.start_x, self.app.start_y, event.x, event.y,
                outline=self.app.current_color, width=self.app.brush_size, dash=(4, 4)
            )

    def on_release(self, event):
        """Handle mouse button release to finalize drawing"""
        # Finalize freehand/eraser stroke
        if self.app.current_tool in ("freehand", "eraser"):
            if self.app.current_stroke_id:
                self.app.history_stack.append(self.app.current_stroke_id)
                self.app.current_stroke_id = None
                self.app.current_stroke_points = []
                self.app.redo_stack.clear()
                self.app.file_ops.update_buttons()
            return

        # Finalize shapes
        item_id = None
        if self.app.current_tool == "line":
            item_id = self._create_final_line(event)
        elif self.app.current_tool == "rectangle":
            item_id = self._create_final_rectangle(event)
        elif self.app.current_tool == "oval":
            item_id = self._create_final_oval(event)

        # Cleanup preview
        if self.preview_id:
            try:
                self.app.canvas.delete(self.preview_id)
            except Exception:
                pass
            self.preview_id = None

        if item_id:
            self.app.history_stack.append(item_id)
            self.app.redo_stack.clear()
            self.app.file_ops.update_buttons()

    def _create_final_line(self, event):
        """Create final line"""
        return self.app.canvas.create_line(
            self.app.start_x, self.app.start_y, event.x, event.y,
            fill=self.app.current_color, width=self.app.brush_size
        )

    def _create_final_rectangle(self, event):
        """Create final rectangle based on fill mode"""
        if self.app.fill_mode == "outline":
            return self.app.canvas.create_rectangle(
                self.app.start_x, self.app.start_y, event.x, event.y,
                outline=self.app.current_color, width=self.app.brush_size
            )
        elif self.app.fill_mode == "filled":
            return self.app.canvas.create_rectangle(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline=self.app.current_color, 
                width=self.app.brush_size
            )
        else:  # both
            return self.app.canvas.create_rectangle(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline="black", width=self.app.brush_size
            )

    def _create_final_oval(self, event):
        """Create final oval based on fill mode"""
        if self.app.fill_mode == "outline":
            return self.app.canvas.create_oval(
                self.app.start_x, self.app.start_y, event.x, event.y,
                outline=self.app.current_color, width=self.app.brush_size
            )
        elif self.app.fill_mode == "filled":
            return self.app.canvas.create_oval(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline=self.app.current_color, 
                width=self.app.brush_size
            )
        else:  # both
            return self.app.canvas.create_oval(
                self.app.start_x, self.app.start_y, event.x, event.y,
                fill=self.app.current_color, outline="black", width=self.app.brush_size
            )

    def on_motion(self, event):
        """Handle mouse motion to update status with coordinates"""
        self.app.ui.update_status(f" | Pos: {event.x},{event.y}")
