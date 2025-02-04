import json
from abc import ABC, abstractmethod
import fitz

class TextExtractionStrategy(ABC):
    @abstractmethod
    def can_handle(self, rectangle_data, doc) -> bool:
        pass
        
    @abstractmethod
    def extract_text(self, rectangle_data, doc) -> dict:
        pass

class TextExtractionManager:
    def __init__(self, pdf_path, json_path):
        """
        pdf_path: ścieżka do pliku PDF
        json_path: ścieżka do pliku rectangle_map.json
        """
        self.pdf_path = pdf_path
        self.json_path = json_path
        self.doc = fitz.open(pdf_path)
        self.strategies = []

    def register_strategy(self, strategy: TextExtractionStrategy):
        """Dodaje nową strategię do managera"""
        self.strategies.append(strategy)

    def process_rectangle(self, rectangle_data):
        """
        Przetwarza pojedynczy prostokąt używając odpowiedniej strategii
        """
        print(f"Processing rectangle ID: {rectangle_data['id']}")
        
        for strategy in self.strategies:
            try:
                if strategy.can_handle(rectangle_data, self.doc):
                    print(f"Using strategy: {strategy.__class__.__name__}")
                    result = strategy.extract_text(rectangle_data, self.doc)
                    self.save_results(rectangle_data, result)
                    return True
            except Exception as e:
                print(f"Strategy {strategy.__class__.__name__} failed: {e}")
                continue
                
        print(f"No suitable strategy found for rectangle {rectangle_data['id']}")
        return False

    def save_results(self, rectangle_data, extraction_results):
        """
        Zapisuje wyniki ekstrakcji do pliku JSON
        """
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
                
            # Znajdź i zaktualizuj odpowiedni prostokąt
            for rect in data.get('rectangles', []):
                if rect['id'] == rectangle_data['id']:
                    rect.update({
                        'extracted_text': extraction_results['text'],
                        'extraction_source': extraction_results['source'],
                        'extraction_metadata': extraction_results.get('metadata', {}),
                        'extraction_status': 'completed'
                    })
                    break
                    
            # Zapisz zaktualizowane dane
            with open(self.json_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"Results saved for rectangle {rectangle_data['id']}")
            
        except Exception as e:
            print(f"Error saving results: {e}")

    def process_pending(self):
        """
        Przetwarza wszystkie oczekujące prostokąty
        """
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
            
            for rect in data.get('rectangles', []):
                if 'extraction_status' not in rect:
                    self.process_rectangle(rect)
                    
        except Exception as e:
            print(f"Error processing pending rectangles: {e}")

    def __del__(self):
        """Cleanup przy usuwaniu managera"""
        if hasattr(self, 'doc'):
            self.doc.close()