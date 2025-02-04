import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

from pdf_viewer_ui import PDFViewerUI
from pdf_navigation import PDFNavigation
from screenshot_manager import ScreenshotManager
from screenshot_list import ScreenshotList
from rectangle_manager import RectangleManager
from data_persistence import DataManager
from rectangle_processor import RectangleProcessor

class PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Annotator")
        self.root.state("zoomed")  # Start maximized
        
        # Initialize Data Manager
        self.data_manager = DataManager()
        self.rectangle_processor = None
        
        self.setup_menu()
        self.setup_ui()
        
        # Bind window closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start with file dialog
        self.open_pdf_file()
        
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF...", command=self.open_pdf_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export Project...", command=self.export_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
    def setup_ui(self):
        """Setup main UI components"""
        # Create main horizontal split
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for PDF viewer
        self.left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame, weight=3)
        
        # Right frame for screenshot list
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=1)
        
        # Status bar frame
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status bar
        self.status_bar = ttk.Label(status_frame, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        # Processing status
        self.processing_status = ttk.Label(status_frame, relief=tk.SUNKEN, width=50, anchor=tk.E)
        self.processing_status.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def update_status(self, message):
        """Update status bar message"""
        if message.startswith("Processing") or message.startswith("Rectangle Processor"):
            self.processing_status.config(text=message)
        else:
            self.status_bar.config(text=message)
        
    def initialize_with_pdf(self, pdf_path):
        """Initialize application with a PDF file"""
        try:
            # Initialize project
            project = self.data_manager.init_project(pdf_path)
            
            # Stop existing processor if any
            if self.rectangle_processor:
                self.rectangle_processor.stop()
            
            # Start new processor with status callback
            self.rectangle_processor = RectangleProcessor(
                project['data_file'],  # json_path
                project['pdf_path'],   # pdf_path
                self.update_status     # callback
            )
            
            # Clear existing widgets
            for widget in self.left_frame.winfo_children():
                widget.destroy()
            for widget in self.right_frame.winfo_children():
                widget.destroy()
            
            # Initialize components
            navigation = PDFNavigation(self.left_frame, pdf_path)
            self.pdf_viewer = PDFViewerUI(self.left_frame, navigation)
            self.navigation = navigation  # zachowujemy referencję

            self.screenshot_manager = ScreenshotManager(project['screenshots_dir'])
            
            # Initialize Screenshot List
            self.screenshot_list = ScreenshotList(
                self.right_frame,
                self.screenshot_manager,
                self.data_manager
            )
            
            # Initialize Rectangle Manager
            self.rectangle_manager = RectangleManager(
                self.pdf_viewer.get_canvas(),
                self.pdf_viewer,
                self.screenshot_manager,
                self.data_manager
            )
            
            # Set screenshot list reference in rectangle manager
            self.rectangle_manager.screenshot_list = self.screenshot_list
            
            # Load existing rectangles
            rectangles = self.data_manager.load_rectangle_data()
            self.rectangle_manager.redraw_rectangles(rectangles)
            self.screenshot_list.update_list(rectangles)
            
            self.update_status(f"Loaded PDF: {os.path.basename(pdf_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            
    def open_pdf_file(self):
        """Open file dialog to select PDF"""
        file_path = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.initialize_with_pdf(file_path)
            
    def export_project(self):
        """Export project to a directory"""
        if not hasattr(self, 'data_manager') or not self.data_manager.current_project:
            messagebox.showwarning("Warning", "No project to export")
            return
            
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if export_dir:
            try:
                output_dir = self.data_manager.export_project(export_dir)
                messagebox.showinfo(
                    "Success",
                    f"Project exported successfully to:\n{output_dir}"
                )
                self.update_status("Project exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export project: {str(e)}")
                
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        
    def on_closing(self):
        """Handle application closing"""
        if self.rectangle_processor:
            self.rectangle_processor.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()