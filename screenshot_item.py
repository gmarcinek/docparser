import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ScreenshotItem(ttk.Frame):
    def __init__(self, parent, thumbnail_path, page_num, rect_id, description="", 
                 on_delete=None, on_thumbnail_click=None):
        super().__init__(parent)
        self.rect_id = rect_id
        self.page_num = page_num
        self.on_delete = on_delete
        self.on_thumbnail_click = on_thumbnail_click
        
        self.pack(fill=tk.X, padx=5, pady=2)
        
        # Delete button frame
        delete_btn = ttk.Button(self, text="X", width=2, command=self._on_delete)
        delete_btn.pack(side=tk.LEFT, padx=(0,2))
        
        # Thumbnail frame
        self.thumb_frame = ttk.Frame(self, width=80, height=80, style='Thumb.TFrame')
        self.thumb_frame.pack(side=tk.LEFT, padx=2)
        self.thumb_frame.pack_propagate(False)
        
        # Style configuration
        style = ttk.Style()
        style.configure('Thumb.TFrame', background='lightgray', borderwidth=1, relief='solid')
        style.configure('Screenshot.TLabel', font=('Arial', 10))
        
        # Thumbnail label
        self.thumb_label = ttk.Label(self.thumb_frame, cursor="hand2")
        self.thumb_label.pack(expand=True, fill=tk.BOTH)
        self.thumb_label.bind("<Button-1>", self._on_thumbnail_click)
        
        # Load thumbnail
        if os.path.exists(thumbnail_path):
            try:
                with Image.open(thumbnail_path) as img:
                    photo = ImageTk.PhotoImage(img)
                    self.thumb_label.configure(image=photo)
                    self.thumb_label.image = photo
            except Exception as e:
                self.thumb_label.configure(text="No image")
        else:
            self.thumb_label.configure(text="No image")

        # Content frame with flex
        content_frame = ttk.Frame(self)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Info labels in horizontal layout
        ttk.Label(content_frame, text=f"Strona: {page_num+1}", style='Screenshot.TLabel').pack(side=tk.LEFT)
        ttk.Label(content_frame, text=f"ID: {rect_id}", style='Screenshot.TLabel').pack(side=tk.LEFT, padx=10)
        
        if description:
            desc_label = ttk.Label(content_frame, text=description, wraplength=300, style='Screenshot.TLabel')
            desc_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
    def _on_delete(self):
        if self.on_delete:
            self.on_delete(self.rect_id)
            
    def _on_thumbnail_click(self, event):
        if self.on_thumbnail_click:
            self.on_thumbnail_click("thumbnail_click", {"id": self.rect_id, "page": self.page_num})