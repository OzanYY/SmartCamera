class TextureDrawer:
    def __init__(self, texture=None):
        """
        Инициализация рисовальщика текстуры

        Args:
            texture: Данные существующей текстуры (numpy array)
        """

        # Если переданы данные текстуры
        if texture.any():
            self.texture_data = texture.copy()
            self.width = texture.shape[1]
            self.height = texture.shape[0]
        else:
            self.texture_data = None
            self.width = 0
            self.height = 0

    def clear(self, color=(0, 0, 0, 1)):
        """Очистить текстуру цветом"""
        self.texture_data[:, :] = color
        return self.texture_data


    def draw_pixel(self, x, y, color):
        """Нарисовать пиксель"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.texture_data[y, x] = color
        return self.texture_data

    def draw_circle(self, center_x, center_y, radius, color, thickness=1, fill=None):
        """
        Нарисовать круг с использованием алгоритма Брезенхема

        Args:
            center_x: X координата центра
            center_y: Y координата центра
            radius: Радиус окружности
            color: Цвет контура в формате [R, G, B, A] (0-255)
            thickness: Толщина линии контура (пиксели)
            fill: Цвет заливки в формате [R, G, B, A] (0-255) или None
        """
        # Конвертируем цвета
        color_norm = [c / 255.0 for c in color] if len(color) > 0 else [0, 0, 0, 1]

        if fill is not None:
            fill_norm = [c / 255.0 for c in fill] if len(fill) > 0 else color_norm

        # Ограничиваем координаты
        cx, cy = int(center_x), int(center_y)
        r = int(radius)
        t = max(1, int(thickness))

        # Если нужна заливка, сначала заливаем весь круг
        if fill is not None:
            for y in range(max(0, cy - r), min(self.height, cy + r + 1)):
                for x in range(max(0, cx - r), min(self.width, cx + r + 1)):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                        self.texture_data[y, x] = fill_norm

        # Рисуем контур с заданной толщиной
        for current_thickness in range(t):
            current_radius = r - current_thickness
            if current_radius < 0:
                continue

            # Алгоритм Брезенхема для рисования окружности
            x = 0
            y = current_radius
            d = 3 - 2 * current_radius

            while y >= x:
                # Рисуем 8 симметричных точек
                points = [
                    (cx + x, cy + y), (cx - x, cy + y),
                    (cx + x, cy - y), (cx - x, cy - y),
                    (cx + y, cy + x), (cx - y, cy + x),
                    (cx + y, cy - x), (cx - y, cy - x)
                ]

                for px, py in points:
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.texture_data[py, px] = color_norm

                x += 1

                if d > 0:
                    y -= 1
                    d = d + 4 * (x - y) + 10
                else:
                    d = d + 4 * x + 6

        return self.texture_data


    def draw_line(self, x1, y1, x2, y2, color, thickness=1):
        """Нарисовать линию (алгоритм Брезенхэма)"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            for dy_t in range(-thickness // 2, thickness // 2 + 1):
                for dx_t in range(-thickness // 2, thickness // 2 + 1):
                    ny = y1 + dy_t
                    nx = x1 + dx_t
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.texture_data[ny, nx] = color

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return self.texture_data

    def draw_rectangle(self, x1, y1, x2, y2, color, thickness=1, fill=None):
        """
        Нарисовать прямоугольник

        Args:
            x1, y1: Координаты первого угла
            x2, y2: Координаты противоположного угла
            color: Цвет контура в формате [R, G, B, A] (0-255)
            thickness: Толщина линии контура
            fill: Цвет заливки в формате [R, G, B, A] (0-255) или None
        """
        # Убедимся, что x1,y1 - левый верхний, x2,y2 - правый нижний
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        # Заливка прямоугольника
        if fill is not None:
            # Конвертируем цвет заливки
            fill_norm = [c / 255.0 for c in fill] if len(fill) > 0 else [0, 0, 0, 1]

            # Заполняем область прямоугольника
            for y in range(int(top), int(bottom) + 1):
                for x in range(int(left), int(right) + 1):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.texture_data[y, x] = fill_norm

        # Рисуем 4 стороны прямоугольника
        # Верхняя сторона
        self.draw_line(left, top, right, top, color, thickness)
        # Правая сторона
        self.draw_line(right, top, right, bottom, color, thickness)
        # Нижняя сторона
        self.draw_line(left, bottom, right, bottom, color, thickness)
        # Левая сторона
        self.draw_line(left, top, left, bottom, color, thickness)

        return self.texture_data


    def draw_text(self, x, y, text, color, scale=1, font="simple"):
        """
        Нарисовать текст

        Args:
            x, y: Координаты левого верхнего угла текста
            text: Строка текста для отрисовки
            color: Цвет текста в формате [R, G, B, A] (0-255)
            scale: Масштаб текста
            font: Используемый шрифт ("simple", "small")
        """
        # Конвертируем цвет
        color_norm = [c / 255.0 for c in color] if len(color) > 0 else [0, 0, 0, 1]

        # Словарь простого шрифта 5x7 пикселей
        if font == "simple":
            font_dict = self._get_simple_font()
        elif font == "small":
            font_dict = self._get_small_font()
        else:
            font_dict = self._get_simple_font()

        current_x = int(x)
        current_y = int(y)
        char_width = 6 * scale
        char_height = 8 * scale

        for char in text:
            if char == '\n':
                current_x = int(x)
                current_y += char_height
                continue
            elif char == ' ':
                current_x += char_width
                continue

            # Получаем битовую карту символа
            if char in font_dict:
                bitmap = font_dict[char]
                self._draw_char_bitmap(current_x, current_y, bitmap, color_norm, scale)

            current_x += char_width

        return self.texture_data


    def _get_simple_font(self):
        """Простой шрифт 5x7 пикселей"""
        # Каждый символ представлен как список из 7 чисел (битовая маска)
        font = {
            'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
            'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
            'C': [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
            'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
            'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
            'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
            'G': [0x0E, 0x11, 0x10, 0x13, 0x11, 0x11, 0x0F],
            'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
            'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
            'J': [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
            'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
            'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
            'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
            'N': [0x11, 0x19, 0x19, 0x15, 0x13, 0x13, 0x11],
            'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
            'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
            'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
            'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
            'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
            'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
            'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
            'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
            'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
            'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
            'a': [0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F],
            'b': [0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x1E],
            'c': [0x00, 0x00, 0x0E, 0x10, 0x10, 0x11, 0x0E],
            'd': [0x01, 0x01, 0x0D, 0x13, 0x11, 0x11, 0x0F],
            'e': [0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E],
            'f': [0x02, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x04],
            'g': [0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E],
            'h': [0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x11],
            'i': [0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E],
            'j': [0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C],
            'k': [0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12],
            'l': [0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
            'm': [0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15],
            'n': [0x00, 0x00, 0x16, 0x19, 0x11, 0x11, 0x11],
            'o': [0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E],
            'p': [0x00, 0x00, 0x1E, 0x11, 0x1E, 0x10, 0x10],
            'q': [0x00, 0x00, 0x0D, 0x13, 0x0F, 0x01, 0x01],
            'r': [0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10],
            's': [0x00, 0x00, 0x0E, 0x10, 0x0E, 0x01, 0x1E],
            't': [0x04, 0x04, 0x0E, 0x04, 0x04, 0x04, 0x02],
            'u': [0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D],
            'v': [0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04],
            'w': [0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x0A],
            'x': [0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11],
            'y': [0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E],
            'z': [0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F],
            '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
            '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
            '2': [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
            '3': [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
            '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
            '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
            '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
            '7': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
            '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
            '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
            '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
            ',': [0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C, 0x04],
            '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
            '?': [0x0E, 0x11, 0x02, 0x04, 0x04, 0x00, 0x04],
            ':': [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00],
            ';': [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x04],
            '-': [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
            '_': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F],
            '+': [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
            '=': [0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00],
            '(': [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
            ')': [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
            '[': [0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E],
            ']': [0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E],
            '/': [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x00],
            '\\': [0x00, 0x10, 0x08, 0x04, 0x02, 0x01, 0x00],
            '|': [0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
            '@': [0x0E, 0x11, 0x17, 0x15, 0x17, 0x10, 0x0F],
            '#': [0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A],
            '$': [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
            '%': [0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03],
            '^': [0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00],
            '&': [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
            '*': [0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00],
            '"': [0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00],
            "'": [0x04, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00],
            '<': [0x00, 0x02, 0x04, 0x08, 0x04, 0x02, 0x00],
            '>': [0x00, 0x08, 0x04, 0x02, 0x04, 0x08, 0x00],
        }
        return font


    def _get_small_font(self):
        """Маленький шрифт 3x5 пикселей"""
        font = {
            'A': [0x0E, 0x11, 0x1F, 0x11, 0x11],
            'B': [0x1E, 0x11, 0x1E, 0x11, 0x1E],
            'C': [0x0E, 0x11, 0x10, 0x11, 0x0E],
            '0': [0x0E, 0x11, 0x11, 0x11, 0x0E],
            '1': [0x04, 0x0C, 0x04, 0x04, 0x0E],
            '2': [0x0E, 0x01, 0x0E, 0x10, 0x1F],
            '3': [0x0E, 0x01, 0x06, 0x01, 0x0E],
            '4': [0x11, 0x11, 0x1F, 0x01, 0x01],
            '5': [0x1F, 0x10, 0x1E, 0x01, 0x1E],
            '6': [0x0E, 0x10, 0x1E, 0x11, 0x0E],
            '7': [0x1F, 0x01, 0x02, 0x04, 0x04],
            '8': [0x0E, 0x11, 0x0E, 0x11, 0x0E],
            '9': [0x0E, 0x11, 0x0F, 0x01, 0x0E],
            '.': [0x00, 0x00, 0x00, 0x00, 0x04],
            ':': [0x00, 0x04, 0x00, 0x04, 0x00],
            '-': [0x00, 0x00, 0x0E, 0x00, 0x00],
        }
        return font


    def _draw_char_bitmap(self, x, y, bitmap, color, scale=1):
        """Нарисовать символ по битовой карте"""
        height = len(bitmap)
        width = 5  # для шрифта 5x7

        for row in range(height):
            row_bits = bitmap[row]
            for col in range(width):
                if row_bits & (1 << (width - 1 - col)):
                    # Рисуем пиксель с учетом масштаба
                    for sy in range(scale):
                        for sx in range(scale):
                            px = x + col * scale + sx
                            py = y + row * scale + sy
                            if 0 <= px < self.width and 0 <= py < self.height:
                                self.texture_data[py, px] = color