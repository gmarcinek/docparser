import fitz
import json
import os

class PDFTextExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.output_dir = None  # będzie ustawione później
        
    def extract_full_text(self):
        """Ekstrahuje pełny tekst z dokumentu z zachowaniem struktury"""
        document_structure = []
        
        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]
            
            # Pobierz bloki tekstu z informacją o formatowaniu
            blocks = page.get_text("dict")["blocks"]
            
            page_content = []
            for block in blocks:
                if block["type"] == 0:  # text block
                    content = {
                        "type": "text",
                        "bbox": block["bbox"],
                        "lines": []
                    }
                    
                    for line in block["lines"]:
                        line_content = {
                            "bbox": line["bbox"],
                            "spans": []
                        }
                        
                        for span in line["spans"]:
                            line_content["spans"].append({
                                "text": span["text"],
                                "font": span["font"],
                                "size": span["size"],
                                "flags": span["flags"],  # bold, italic etc.
                                "bbox": span["bbox"]
                            })
                            
                        content["lines"].append(line_content)
                        
                    page_content.append(content)
                elif block["type"] == 1:  # image block
                    page_content.append({
                        "type": "image",
                        "bbox": block["bbox"]
                    })
                    
            document_structure.append({
                "page": page_num + 1,
                "content": page_content
            })
        
        # Zapisz strukturę do JSON
        output_path = os.path.join(self.output_dir, 'pdf_content.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(document_structure, f, indent=2, ensure_ascii=False)
            
        # Zapisz też wersję plain text
        text_output = os.path.join(self.output_dir, 'pdf_content.txt')
        with open(text_output, 'w', encoding='utf-8') as f:
            for page in document_structure:
                f.write(f"\n=== Page {page['page']} ===\n")
                for block in page['content']:
                    if block['type'] == 'text':
                        for line in block['lines']:
                            for span in line['spans']:
                                f.write(span['text'] + ' ')
                            f.write('\n')
                f.write('\n')
                
        return output_path

    def __del__(self):
        if hasattr(self, 'doc'):
            self.doc.close()