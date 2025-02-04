import json
import os
from datetime import datetime
from extractors.pdf_text_extractor import PDFTextExtractor
from extractors.pdf_table_extractor import PDFTableExtractor
from extractors.pdf_rectangle_extractor import PDFRectangleExtractor

class DataManager:
    def __init__(self, project_dir="pdf_projects"):
        print(f"Initializing DataManager with project_dir: {project_dir}")  # Debug log
        self.project_dir = project_dir
        self.current_project = None
        os.makedirs(project_dir, exist_ok=True)
        
    def init_project(self, pdf_path):
        pdf_name = os.path.basename(pdf_path)
        project_name = f"{os.path.splitext(pdf_name)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_path = os.path.join(self.project_dir, project_name)
        
        self.current_project = {
            'name': project_name,
            'path': project_path,
            'pdf_path': pdf_path,
            'screenshots_dir': os.path.join(project_path, 'screenshots'),
            'data_file': os.path.join(project_path, 'rectangle_map.json'),
            'thumbnails_dir': os.path.join(project_path, 'screenshots', 'thumbnails'),
            'rectangles': []
        }
        
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(self.current_project['screenshots_dir'], exist_ok=True)
        os.makedirs(self.current_project['thumbnails_dir'], exist_ok=True)
        
        # Tu dodajemy ekstrakcję
        extractor = PDFTextExtractor(pdf_path)
        extractor.output_dir = project_path
        extractor.extract_full_text()
        
        self.save_rectangle_data([])
        
        return self.current_project

    def save_rectangle_data(self, rectangles):
        """Save rectangle data to JSON file"""
        if not self.current_project:
            raise ValueError("No project initialized")
            
        data = {
            'pdf_path': self.current_project['pdf_path'],
            'rectangles': rectangles
        }
        
        print(f"Saving rectangle data to {self.current_project['data_file']}")  # Debug log
        print(f"Data to save: {data}")  # Debug log
        
        try:
            with open(self.current_project['data_file'], 'w') as f:
                json.dump(data, f, indent=2)
            print("Successfully saved rectangle data")  # Debug log
        except Exception as e:
            print(f"Error saving rectangle data: {e}")  # Error log
            raise

    def load_rectangle_data(self):
        """Load rectangle data from JSON file"""
        if not self.current_project:
            raise ValueError("No project initialized")
            
        try:
            with open(self.current_project['data_file'], 'r') as f:
                data = json.load(f)
                print(f"Loaded rectangle data: {data}")  # Debug log
                return data['rectangles']
        except FileNotFoundError:
            print("No existing rectangle data found")  # Debug log
            return []
        except Exception as e:
            print(f"Error loading rectangle data: {e}")  # Error log
            return []

    def add_rectangle(self, rect_info):
        """Add new rectangle data"""
        print(f"Adding new rectangle: {rect_info}")  # Debug log
        rectangle_data = {
            'id': rect_info['id'],
            'page': rect_info['page'],
            'rect': rect_info['rect'],
            'dimensions': {
                'width': rect_info['rect'][2] - rect_info['rect'][0],
                'height': rect_info['rect'][3] - rect_info['rect'][1]
            },
            'description': rect_info.get('description', ''),
            'keywords': rect_info.get('keywords', []),
            'image_path': rect_info.get('image_path', ''),
            'thumbnail_path': rect_info.get('thumbnail_path', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        rectangles = self.load_rectangle_data()
        rectangles.append(rectangle_data)
        self.save_rectangle_data(rectangles)
        return rectangle_data

    def delete_rectangle(self, rect_id, page):
        """Delete rectangle data by ID and page"""
        print(f"Deleting rectangle with ID {rect_id} on page {page}")
        
        # Load current data
        rectangles = self.load_rectangle_data()
        print(f"Current rectangles count: {len(rectangles)}")
        
        # Filter out the rectangle to delete
        new_rectangles = [r for r in rectangles if not (r['id'] == rect_id and r['page'] == page)]
        print(f"Rectangles count after deletion: {len(new_rectangles)}")
        
        # Save updated data
        self.save_rectangle_data(new_rectangles)
        print("Rectangle data updated")
    
    def export_project(self, export_path):
        """Export entire project to a specified location"""
        if not self.current_project:
            raise ValueError("No project to export")
            
        print(f"Exporting project to: {export_path}")  # Debug log
        
        # Create export directory
        export_dir = os.path.join(export_path, self.current_project['name'])
        os.makedirs(export_dir, exist_ok=True)
        
        # Copy PDF file
        import shutil
        shutil.copy2(self.current_project['pdf_path'], export_dir)
        
        # Copy JSON data
        shutil.copy2(self.current_project['data_file'], export_dir)
        
        # Copy screenshots
        screenshots_export_dir = os.path.join(export_dir, 'screenshots')
        os.makedirs(screenshots_export_dir, exist_ok=True)
        
        # Copy thumbnails
        thumbnails_source_dir = os.path.join(os.path.dirname(self.current_project['data_file']), 'screenshots', 'thumbnails')
        thumbnails_export_dir = os.path.join(screenshots_export_dir, 'thumbnails')
        
        # Kopiowanie całego katalogu z miniaturkami
        if os.path.exists(thumbnails_source_dir):
            shutil.copytree(thumbnails_source_dir, thumbnails_export_dir)
        
        rectangles = self.load_rectangle_data()
        for rect in rectangles:
            if rect.get('image_path') and os.path.exists(rect['image_path']):
                shutil.copy2(rect['image_path'], screenshots_export_dir)
        
        print(f"Project successfully exported to {export_dir}")  # Debug log
        return export_dir