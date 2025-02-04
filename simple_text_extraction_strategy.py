import fitz

class SimpleTextExtractionStrategy:

    def can_handle(self, rectangle_data, doc):
        page = doc[rectangle_data['page']]
        rect = fitz.Rect(rectangle_data['rect'])
        text = page.get_text("text", clip=rect)
        print(f"Found text in rectangle: {text}")  # Debug
        return len(text.strip()) > 0

    def extract_text(self, rectangle_data, doc):
        page = doc[rectangle_data['page']]
        rect = fitz.Rect(rectangle_data['rect'])
        text = page.get_text("text", clip=rect)
        result = {
            'text': text.strip(),
            'source': 'pdf_text',
            'metadata': {
                'strategy': 'simple_text',
                'confidence': 1.0
            }
        }
        print(f"Extracted text: {result}")  # Debug
        return result