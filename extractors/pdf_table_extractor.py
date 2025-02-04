import fitz
import json
import os

class PDFTableExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.output_dir = None  # będzie ustawione później
    
    def extract_full_text(self):
        """Ekstrahuje pełny tekst z dokumentu z zachowaniem struktury i wykrywaniem tabel"""
        document_structure = []
        
        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            page_content = []
            potential_table_rows = []
            
            for block in blocks:
                if block["type"] == 0:  # text block
                    bbox = block["bbox"]
                    text_lines = []
                    
                    for line in block["lines"]:
                        line_text = " ".join([span["text"] for span in line["spans"]])
                        text_lines.append((line_text, line["bbox"]))
                    
                    # Wykrywanie potencjalnych tabel (porównujemy współrzędne linii)
                    if potential_table_rows and abs(bbox[1] - potential_table_rows[-1]["bbox"][1]) < 10:
                        potential_table_rows.append({"text": text_lines, "bbox": bbox})
                    else:
                        if len(potential_table_rows) > 1:  # Jeśli mamy kilka wierszy, traktujemy je jako tabelę
                            page_content.append({"type": "table", "rows": potential_table_rows})
                        potential_table_rows = [{"text": text_lines, "bbox": bbox}]
                    
                elif block["type"] == 1:  # image block
                    page_content.append({"type": "image", "bbox": block["bbox"]})
            
            if len(potential_table_rows) > 1:
                page_content.append({"type": "table", "rows": potential_table_rows})
            
            document_structure.append({
                "page": page_num + 1,
                "content": page_content
            })
        
        output_path = os.path.join(self.output_dir, 'pdf_content.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(document_structure, f, indent=2, ensure_ascii=False)
        
        text_output = os.path.join(self.output_dir, 'pdf_content.txt')
        with open(text_output, 'w', encoding='utf-8') as f:
            for page in document_structure:
                f.write(f"\n=== Page {page['page']} ===\n")
                for block in page['content']:
                    if block['type'] == 'text':
                        for line, _ in block['lines']:
                            f.write(line + '\n')
                    elif block['type'] == 'table':
                        f.write("\n[TABLE]\n")
                        for row in block['rows']:
                            row_text = " | ".join([t for t, _ in row['text']])
                            f.write(row_text + '\n')
                f.write('\n')
        
        return output_path

    def __del__(self):
        if hasattr(self, 'doc'):
            self.doc.close()
