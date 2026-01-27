import cv2

class Webcam:
     def __init__(self):
         # Идентификатор и состояние
         self.camera_id = 0  # ID камеры (0 для встроенной)
         self.is_opened = False  # Флаг открытия камеры
         self.cap = None  # Объект захвата видео

         # Параметры изображения
         self.width = 640  # Ширина кадра
         self.height = 480  # Высота кадра
         self.fps = 30  # Кадров в секунду

         # Текущий кадр
         self.current_frame = None  # Текущий захваченный кадр
         self.frame_count = 0  # Счетчик кадров

         # Калибровка и коррекция
         self.camera_matrix = None  # Матрица камеры
         self.dist_coeffs = None  # Коэффициенты дисторсии
         self.calibrated = False  # Флаг калибровки

