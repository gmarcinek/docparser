import fitz
from extractors.pdf_rectangle_extractor import PDFRectangleExtractor

class SimpleTextExtractionStrategy:
    def __init__(self, pdf_path):
        # Użyj PDFTextExtractor do ekstrakcji pełnego tekstu
        self.pdf_extractor = PDFRectangleExtractor(pdf_path)
    
    def can_handle(self, rectangle_data, doc):
        page = doc[rectangle_data['page']]
        rect = fitz.Rect(rectangle_data['rect'])
        text = page.get_text("text", clip=rect)
        print(f"Found text in rectangle: {text}")  # Debug
        return len(text.strip()) > 0

    def extract_text(self, rectangle_data, doc):
        """
        Integruje zaawansowaną ekstrakcję tekstu z PDFTextExtractor w celu uzyskania pełnej struktury.
        """
        page_num = rectangle_data['page']
        rect = fitz.Rect(rectangle_data['rect'])

        # Użyj PDFTextExtractor do wydobycia pełnego tekstu z określonego prostokąta
        extracted_data = self.pdf_extractor.extract_full_text_for_rectangle(page_num, rect)
        
        result = {
            'text': extracted_data['text'].strip(),
            'source': 'pdf_text',
            'metadata': {
                'strategy': 'simple_text',
                'confidence': 1.0
            }
        }
        
        print(f"Extracted text: {result}")  # Debug
        return result
