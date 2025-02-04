import fitz
from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import messagebox

class PDFNavigation:
    def __init__(self, parent, pdf_path):
        self.parent = parent
        self.pdf_path = pdf_path
        self._doc = fitz.open(pdf_path)
        self.page_count = self._doc.page_count
        self.current_page = 0
        self.zoom_level = 1.0  # będzie zaktualizowane później
        self.search_text = None
        self.search_results = []
        self.current_search_index = -1
        
        # These will be set by UI class
        self.canvas = None
        self.page_label = None
        self.canvas_frame = None
        
        self.setup_keyboard_bindings()

    def after_ui_init(self):
        """Call this after UI is initialized to set proper zoom"""
        self.parent.update_idletasks()  # make sure we have correct window dimensions
        self.set_fit_zoom()
        
    def set_canvas(self, canvas):
        self.canvas = canvas
        
    def set_page_label(self, label):
        self.page_label = label
        
    def set_canvas_frame(self, frame):
        self.canvas_frame = frame

    def setup_keyboard_bindings(self):
        # Basic navigation
        self.parent.bind_all('<Left>', lambda e: self.prev_page())
        self.parent.bind_all('<Right>', lambda e: self.next_page())
        self.parent.bind_all('<Prior>', lambda e: self.prev_page())  # Page Up
        self.parent.bind_all('<Next>', lambda e: self.next_page())   # Page Down
        self.parent.bind_all('<Home>', lambda e: self.goto_page(0))
        self.parent.bind_all('<End>', lambda e: self.goto_page(self.page_count - 1))
        
        # Scrolling
        self.parent.bind_all('<Up>', lambda e: self.scroll_vertical(-1))
        self.parent.bind_all('<Down>', lambda e: self.scroll_vertical(1))
        self.parent.bind_all('<Shift-Up>', lambda e: self.scroll_vertical(-5))
        self.parent.bind_all('<Shift-Down>', lambda e: self.scroll_vertical(5))
        
        # Zoom controls
        self.parent.bind_all('<Control-plus>', lambda e: self.zoom_in())
        self.parent.bind_all('<Control-minus>', lambda e: self.zoom_out())
        self.parent.bind_all('<Control-Up>', lambda e: self.zoom_in())
        self.parent.bind_all('<Control-Down>', lambda e: self.zoom_out())
        self.parent.bind_all('<Control-0>', lambda e: self.reset_zoom())

    def load_page(self, page_number):
        """Load and display a page"""
        if not self.canvas:
            return
            
        page = self._doc.load_page(page_number)
        matrix = fitz.Matrix(self.zoom_level * 2, self.zoom_level * 2)
        pix = page.get_pixmap(matrix=matrix)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_tk = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=img_tk, anchor="nw")
        self.canvas.image = img_tk
        
        # Configure canvas scrolling
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update page label
        self.update_page_label()
        
        # Center horizontally
        self.center_pdf()

    def scroll_vertical(self, units):
        """Scroll vertically by given number of units"""
        if self.canvas:
            self.canvas.yview_scroll(units, 'units')

    def center_pdf(self):
        """Center the PDF horizontally in the canvas"""
        if not self.canvas or not self.canvas_frame:
            return
            
        self.canvas.update_idletasks()
        canvas_width = self.canvas_frame.winfo_width()
        pdf_width = self.canvas.bbox("all")[2]
        
        if pdf_width < canvas_width:
            x_offset = (canvas_width - pdf_width) / 2
            self.canvas.configure(scrollregion=(
                -x_offset,
                self.canvas.bbox("all")[1],
                pdf_width + x_offset,
                self.canvas.bbox("all")[3]
            ))

    def goto_page(self, page_num):
        """Go to specific page"""
        if 0 <= page_num < self.page_count:
            self.current_page = page_num
            self.load_page(self.current_page)

    def start_search(self, text):
        """Start new search"""
        self.search_text = text
        self.search_results = []
        self.current_search_index = -1
        self.find_next()

    def find_next(self):
        """Find next occurrence of search text"""
        if not self.search_text:
            return
            
        start_page = self.current_page
        if self.search_results and self.current_search_index < len(self.search_results) - 1:
            self.current_search_index += 1
            return
            
        # Search through pages
        for page_num in range(start_page, self.page_count):
            page = self._doc.load_page(page_num)
            text_instances = page.search_for(self.search_text)
            if text_instances:
                self.goto_page(page_num)
                self.search_results.extend(text_instances)
                self.current_search_index = len(self.search_results) - 1
                return
                
        messagebox.showinfo("Search Complete", "No more occurrences found.")

    def print_pdf(self):
        """Print the PDF"""
        try:
            os.startfile(self.pdf_path, "print")
        except:
            messagebox.showerror("Error", "Unable to print PDF file")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page(self.current_page)

    def next_page(self):
        if self.current_page < self.page_count - 1:
            self.current_page += 1
            self.load_page(self.current_page)

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.load_page(self.current_page)

    def zoom_out(self):
        self.zoom_level *= 0.8
        self.load_page(self.current_page)

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.load_page(self.current_page)

    def update_page_label(self):
        if self.page_label:
            self.page_label.config(
                text=f"Page {self.current_page + 1} of {self.page_count} (Zoom: {int(self.zoom_level * 100)}%)"
            )

    def get_current_page(self):
        return self.current_page

    def get_zoom_level(self):
        return self.zoom_level * 2

    def get_doc(self):
        return self._doc

    def calculate_fit_zoom(self):
        """Calculate zoom level to fit page height in window"""
        if not self.canvas_frame:
            return 1.0

        # Get current window dimensions
        frame_height = self.canvas_frame.winfo_height()
        frame_width = self.canvas_frame.winfo_width()

        # Get current page dimensions at base zoom (1.0)
        page = self._doc.load_page(self.current_page)
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height

        # Calculate zoom factors for both width and height
        width_ratio = (frame_width - 30) / page_width  # -30 for scrollbar and padding
        height_ratio = (frame_height - 30) / page_height

        # Use the smaller ratio to ensure page fits both dimensions
        zoom = min(width_ratio, height_ratio) / 2  # Divide by 2 because we use 2x base zoom in render
        
        print(f"Frame size: {frame_width}x{frame_height}")
        print(f"Page size: {page_width}x{page_height}")
        print(f"Calculated zoom: {zoom}")
        
        return zoom

    def set_fit_zoom(self):
        """Set zoom level to fit page in window"""
        self.zoom_level = self.calculate_fit_zoom()
        self.load_page(self.current_page)