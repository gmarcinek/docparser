import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PDFViewerUI:
    def __init__(self, parent, navigation):
        self.parent = parent
        self.nav = navigation
        self.setup_ui()
        
    def setup_ui(self):
        # Control panel
        self.control_frame = ttk.Frame(self.parent)
        self.control_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        # Navigation buttons
        ttk.Button(self.control_frame, text="Previous", command=self.nav.prev_page).pack(side="left", padx=2)
        ttk.Button(self.control_frame, text="Next", command=self.nav.next_page).pack(side="left", padx=2)
        
        # Zoom controls
        ttk.Button(self.control_frame, text="Zoom In", command=self.nav.zoom_in).pack(side="left", padx=2)
        ttk.Button(self.control_frame, text="Zoom Out", command=self.nav.zoom_out).pack(side="left", padx=2)
        ttk.Button(self.control_frame, text="Reset Zoom", command=self.nav.reset_zoom).pack(side="left", padx=2)
        ttk.Button(self.control_frame, text="Fit to Window", command=self.nav.set_fit_zoom).pack(side="left", padx=2)
        
        # Page indicator
        self.page_label = ttk.Label(self.control_frame, text="")
        self.page_label.pack(side="right", padx=5)
        
        # Canvas with scrollbars
        self.canvas_frame = ttk.Frame(self.parent)
        self.canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Grid layout
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Connect canvas to navigation
        self.nav.set_canvas(self.canvas)
        self.nav.set_page_label(self.page_label)
        self.nav.set_canvas_frame(self.canvas_frame)
        
        # Load initial page
        self.nav.load_page(self.nav.current_page)

        # Load initial page with proper zoom
        self.nav.after_ui_init()  # To na końcu setup_ui

        # Bind resize event
        self.canvas_frame.bind('<Configure>', self.on_resize)

    def on_resize(self, event):
        """Handle window resize"""
        # You might want to add some debouncing here
        if hasattr(self, '_resize_timer'):
            self.parent.after_cancel(self._resize_timer)
        self._resize_timer = self.parent.after(200, self.nav.set_fit_zoom)

    def show_goto_dialog(self):
        """Show dialog for entering page number"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Go to Page")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        dialog.geometry("200x100")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text=f"Enter page number (1-{self.nav.page_count}):").pack(pady=5)
        entry = ttk.Entry(dialog)
        entry.pack(pady=5)
        entry.focus_set()
        
        def validate_and_go():
            try:
                page = int(entry.get())
                if 1 <= page <= self.nav.page_count:
                    self.nav.goto_page(page - 1)  # Convert to 0-based index
                    dialog.destroy()
                else:
                    tk.messagebox.showwarning("Invalid Page", 
                                            f"Please enter a number between 1 and {self.nav.page_count}")
            except ValueError:
                tk.messagebox.showwarning("Invalid Input", "Please enter a valid number")
        
        ttk.Button(dialog, text="Go", command=validate_and_go).pack(pady=5)
        entry.bind('<Return>', lambda e: validate_and_go())
        entry.bind('<Escape>', lambda e: dialog.destroy())

    def show_search_dialog(self):
        """Show search dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Search PDF")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Search text:").pack(pady=5)
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=5)
        entry.focus_set()
        
        def start_search():
            text = entry.get()
            if text:
                self.nav.start_search(text)
                dialog.destroy()
                
        ttk.Button(dialog, text="Search", command=start_search).pack(pady=5)
        entry.bind('<Return>', lambda e: start_search())
        entry.bind('<Escape>', lambda e: dialog.destroy())
    
    def get_canvas(self):
        return self.canvas

    def get_doc(self):
        return self.nav.get_doc()

    def get_current_page(self):
        return self.nav.get_current_page()

    def get_zoom_level(self):
        return self.nav.get_zoom_level()