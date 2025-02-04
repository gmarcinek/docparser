class RectangleManager:
    def __init__(self, canvas, pdf_viewer, screenshot_manager, data_manager):
        self.canvas = canvas
        self.pdf_viewer = pdf_viewer
        self.screenshot_manager = screenshot_manager
        self.data_manager = data_manager
        
        # Stan rysowania
        self.start_x = None
        self.start_y = None
        self.current_rectangle = None
        
        # Minimalne wymiary prostokąta
        self.min_size = 20
        
        self.setup_bindings()
        
    def setup_bindings(self):
        """Ustawienie obsługi zdarzeń myszy"""
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
    def on_press(self, event):
        """Obsługa wciśnięcia przycisku myszy"""
        # Pobierz współrzędne względem zawartości canvasu (uwzględnia scroll)
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.current_rectangle = None
        
    def on_drag(self, event):
        """Obsługa przeciągania myszy"""
        if self.start_x is None:
            return
            
        # Pobierz aktualne współrzędne
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        # Usuń poprzedni tymczasowy prostokąt
        self.canvas.delete("temp_rect")
        
        # Narysuj nowy tymczasowy prostokąt
        self.current_rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            cur_x, cur_y,
            outline="red",
            width=2,
            dash=(5, 5),  # Przerywana linia podczas rysowania
            tags="temp_rect"
        )
        
    def on_release(self, event):
        """Obsługa zwolnienia przycisku myszy"""
        if self.start_x is None:
            return
            
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        # Upewnij się, że współrzędne są w prawidłowej kolejności
        x1, x2 = min(self.start_x, end_x), max(self.start_x, end_x)
        y1, y2 = min(self.start_y, end_y), max(self.start_y, end_y)
        
        # Sprawdź czy prostokąt ma minimalny rozmiar
        if abs(x2 - x1) > self.min_size and abs(y2 - y1) > self.min_size:
            self.create_rectangle([x1, y1, x2, y2])
            
        # Wyczyść tymczasowy prostokąt i zresetuj stan
        self.canvas.delete("temp_rect")
        self.start_x = None
        self.start_y = None
        
    def create_rectangle(self, coords):
        """Utwórz nowy prostokąt i zapisz jego dane"""
        try:
            current_page = self.pdf_viewer.get_current_page()
            
            # Pobierz następne ID prostokąta
            rectangles = self.data_manager.load_rectangle_data()
            next_id = max([r['id'] for r in rectangles], default=0) + 1
            
            # Utwórz podstawowe informacje o prostokącie
            rect_info = {
                'id': next_id,
                'page': current_page,
                'rect': coords
            }
            
            # Zrób i zapisz screenshot zaznaczonego obszaru
            page = self.pdf_viewer.get_doc().load_page(current_page)
            screenshot = self.screenshot_manager.capture_screenshot(
                page, coords, self.pdf_viewer.get_doc(),
                self.pdf_viewer.get_zoom_level()
            )
            
            # Zapisz screenshot i miniaturę
            paths = self.screenshot_manager.save_screenshot(
                screenshot, current_page, next_id
            )
            rect_info['image_path'] = paths['image_path']
            rect_info['thumbnail_path'] = paths['thumbnail_path']
            
            # Zapisz dane prostokąta
            self.data_manager.add_rectangle(rect_info)
            
            # Narysuj prostokąt na canvas
            self.draw_rectangle(rect_info)
            
            # Aktualizuj listę screenshotów jeśli jest dostępna
            if hasattr(self, 'screenshot_list'):
                rectangles = self.data_manager.load_rectangle_data()
                self.screenshot_list.update_list(rectangles)
            
            return rect_info
            
        except Exception as e:
            print(f"Error creating rectangle: {e}")
            raise
        
    def draw_rectangle(self, rect_info):
        """Narysuj stały prostokąt na canvas"""
        coords = rect_info['rect']
        self.canvas.create_rectangle(
            coords[0], coords[1], coords[2], coords[3],
            outline="red",
            width=2,
            tags=f"rect_{rect_info['id']}"
        )
        
    def clear_rectangles(self):
        """Usuń wszystkie prostokąty z canvas"""
        self.canvas.delete("rect")
        
    def redraw_rectangles(self, rectangles):
        """Przerysuj wszystkie prostokąty dla aktualnej strony"""
        self.clear_rectangles()
        current_page = self.pdf_viewer.get_current_page()
        
        for rect in rectangles:
            if rect['page'] == current_page:
                self.draw_rectangle(rect)
                
    def set_screenshot_list(self, screenshot_list):
        """Ustaw referencję do listy screenshotów"""
        self.screenshot_list = screenshot_list