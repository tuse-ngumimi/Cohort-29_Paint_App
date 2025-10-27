"""
Drawing Canvas App 
Project By: Group 17 (Cohort 19 Python Advanced)
Contributor: Ngumimi Bethel Tuse

This is the main entry point that initializes and runs the application.

"""

import tkinter as tk
from ui_components import UIComponents
from drawing_tools import DrawingTools
from file_operations import FileOperations

CANVAS_BG = "white"


class DrawingApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Drawing Canvas App - Group 17")
        self.root.geometry("1000x700")

        # Model / state
        self.current_tool = "freehand"
        self.current_color = "#000000"
        self.brush_size = 4
        self.fill_mode = "outline"

        # Drawing buffers / history
        self.history_stack = []
        self.redo_stack = []
        self.current_stroke_id = None
        self.current_stroke_points = []
        self.start_x = None
        self.start_y = None

        # Initialize modules
        self.ui = UIComponents(self)
        self.drawing = DrawingTools(self)
        self.file_ops = FileOperations(self)

        # Build UI and bind events
        self.ui.build_ui()
        self.drawing.bind_events()


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
