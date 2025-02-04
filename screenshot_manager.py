import os
from PIL import Image
import fitz

class ScreenshotManager:
    def __init__(self, output_dir):
        """Initialize with output directory"""
        print(f"Initializing ScreenshotManager with output_dir: {output_dir}")
        self.output_dir = output_dir
        self.thumbnails_dir = os.path.join(output_dir, "thumbnails")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)

    def capture_screenshot(self, page, rect, doc, zoom_level=2.0):
        """Capture a screenshot from PDF page"""
        print(f"Capturing screenshot with rect: {rect}, zoom_level: {zoom_level}")
        
        # Convert canvas coordinates to PDF coordinates
        pdf_rect = fitz.Rect(
            rect[0] / zoom_level,
            rect[1] / zoom_level,
            rect[2] / zoom_level,
            rect[3] / zoom_level
        )
        
        # Create high-resolution image for OCR (300 DPI)
        matrix = fitz.Matrix(300/72, 300/72)
        try:
            pix = page.get_pixmap(matrix=matrix, clip=pdf_rect)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            print(f"Screenshot captured successfully, size: {img.size}")
            return img
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            raise

    def save_screenshot(self, image, page_num, rect_id):
        """Save screenshot and its thumbnail"""
        # Generate filenames
        screenshot_filename = f"page{page_num+1}_rect{rect_id}.jpg"
        thumbnail_filename = f"page{page_num+1}_rect{rect_id}_thumb.jpg"
        
        screenshot_path = os.path.join(self.output_dir, screenshot_filename)
        thumbnail_path = os.path.join(self.thumbnails_dir, thumbnail_filename)
        
        print(f"Saving files:")
        print(f"- Screenshot: {screenshot_path}")
        print(f"- Thumbnail: {thumbnail_path}")
        
        try:
            # Save high-quality screenshot (300 DPI)
            image.save(screenshot_path, 'JPEG', quality=95, dpi=(300, 300))
            print("Saved screenshot successfully")
            
            # Create and save thumbnail
            thumbnail = self.create_thumbnail(image)
            if thumbnail:
                thumbnail.save(thumbnail_path, 'JPEG', quality=85)
                print("Saved thumbnail successfully")
                
                # Verify files exist
                print(f"Verification:")
                print(f"- Screenshot exists: {os.path.exists(screenshot_path)}")
                print(f"- Thumbnail exists: {os.path.exists(thumbnail_path)}")
                print(f"- Thumbnail size: {thumbnail.size}")
                
                return {
                    'image_path': screenshot_path,
                    'thumbnail_path': thumbnail_path
                }
        except Exception as e:
            print(f"Error saving files: {e}")
            raise

    def create_thumbnail(self, image, max_size=80):
        """Create thumbnail maintaining aspect ratio"""
        try:
            width, height = image.size
            print(f"Creating thumbnail from {width}x{height} image")
            
            # Calculate new dimensions maintaining aspect ratio
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            print(f"New thumbnail dimensions: {new_width}x{new_height}")
            
            # Create thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"Thumbnail created successfully, size: {thumbnail.size}")
            
            return thumbnail
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None

    def delete_screenshot(self, image_path):
        """Delete screenshot and its thumbnail"""
        try:
            print(f"Deleting screenshot: {image_path}")
            
            # Delete screenshot
            if os.path.exists(image_path):
                os.remove(image_path)
                print("Screenshot deleted")
            
            # Delete thumbnail
            thumbnail_path = self.get_thumbnail_path(image_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                print("Thumbnail deleted")
            
            return True
            
        except Exception as e:
            print(f"Error deleting files: {e}")
            return False

    def get_thumbnail_path(self, image_path):
        """Get thumbnail path for a screenshot path"""
        if image_path:
            filename = os.path.basename(image_path)
            name_without_ext = os.path.splitext(filename)[0]
            return os.path.join(self.thumbnails_dir, f"{name_without_ext}_thumb.jpg")
        return None

    def list_screenshots(self):
        """List all screenshots and thumbnails"""
        print("\nCurrent screenshots:")
        print(f"Screenshots directory: {self.output_dir}")
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                if file.endswith('.jpg'):
                    print(f"- {file}")
        
        print("\nThumbnails directory: {self.thumbnails_dir}")
        if os.path.exists(self.thumbnails_dir):
            for file in os.listdir(self.thumbnails_dir):
                if file.endswith('_thumb.jpg'):
                    print(f"- {file}")