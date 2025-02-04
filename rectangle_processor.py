import json
import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue
from text_extraction_manager import TextExtractionManager

class RectangleProcessor:
    def __init__(self, json_path, pdf_path, status_callback=None):
        self.json_path = json_path
        self.pdf_path = pdf_path
        self.processed_ids = set()
        self.event_queue = Queue()
        self.lock = threading.Lock()
        self.status_callback = status_callback
        
        # Initialize TextExtractionManager
        self.extraction_manager = TextExtractionManager(pdf_path, json_path)
        
        self.setup_watcher()
        self.update_status("Rectangle Processor started")

    def update_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def setup_watcher(self):
        self.observer = Observer()
        self.observer.schedule(
            JsonFileHandler(self.on_json_change),
            os.path.dirname(self.json_path),
            recursive=False
        )
        self.observer.start()
        self.update_status("Watching for changes in rectangle_map.json")

    def on_json_change(self):
        time.sleep(0.2)  # Debouncing
        with self.lock:
            try:
                with open(self.json_path, 'r') as f:
                    content = f.read()
                    data = json.loads(content) if content else {"rectangles": []}
            except json.JSONDecodeError:
                self.update_status("Error: Failed to parse JSON file")
                return

            modified = False
            for rect in data.get('rectangles', []):
                if rect['id'] not in self.processed_ids and not rect.get('eventComplete', False):
                    self.event_queue.put(rect)
                    rect['eventComplete'] = True
                    self.processed_ids.add(rect['id'])
                    modified = True
                    self.update_status(f"New rectangle detected: ID {rect['id']}")

            if modified:
                with open(self.json_path, 'w') as f:
                    json.dump(data, f, indent=2)
                self.update_status("Rectangle map updated with processed items")

            self.process_events()

    def process_events(self):
        while not self.event_queue.empty():
            rect = self.event_queue.get()
            self.update_status(f"Processing rectangle ID {rect['id']}")
            try:
                print("Starting text extraction for rectangle:", rect['id'])  # Debug
                result = self.extraction_manager.process_rectangle(rect)
                print("Text extraction result:", result)  # Debug
            except Exception as e:
                self.update_status(f"Error processing rectangle ID {rect['id']}: {e}")

    def stop(self):
        self.update_status("Stopping Rectangle Processor...")
        self.observer.stop()
        self.observer.join()
        self.update_status("Rectangle Processor stopped")

class JsonFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.src_path.endswith('rectangle_map.json'):
            self.callback()