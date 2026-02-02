import numpy as np

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
