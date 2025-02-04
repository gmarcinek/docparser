import tkinter as tk
from tkinter import ttk
from screenshot_item import ScreenshotItem

class ScreenshotList:
    def __init__(self, parent, screenshot_manager, data_manager):
        self.parent = parent
        self.screenshot_manager = screenshot_manager
        self.data_manager = data_manager
        self.items = {}
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.parent, text="Screenshots", font=('Arial', 12, 'bold')).pack(side="top", pady=5)

        # Scrollable canvas
        self.canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        
        self.items_frame = ttk.Frame(self.canvas)
        self.items_frame.bind("<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.items_frame, anchor="nw", 
                                width=self.parent.winfo_width())
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_list(self, rectangles):
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.items.clear()

        # Create new items
        for rect in sorted(rectangles, key=lambda x: (x['page'], x['id'])):
            item = ScreenshotItem(
                self.items_frame,
                rect.get('thumbnail_path', ''),
                rect['page'],
                rect['id'],
                rect.get('description', ''),
                self._on_item_delete,
                self._on_thumbnail_click
            )
            self.items[rect['id']] = item
            
    def _on_item_delete(self, rect_id):
        rectangles = self.data_manager.load_rectangle_data()
        rect_to_delete = next((r for r in rectangles if r['id'] == rect_id), None)
        
        if rect_to_delete and 'image_path' in rect_to_delete:
            self.screenshot_manager.delete_screenshot(rect_to_delete['image_path'])
            
        if rect_id in self.items:
            self.items[rect_id].destroy()
            del self.items[rect_id]
            
        new_rectangles = [r for r in rectangles if r['id'] != rect_id]
        self.data_manager.save_rectangle_data(new_rectangles)

    def _on_thumbnail_click(self, event_type, data):
        self.parent.event_generate("<<ThumbnailClick>>", data=str(data))