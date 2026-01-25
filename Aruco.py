import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict, Union
import json


class ArucoMarkerDetector:
    """
    Класс для работы с ArUco маркерами
    """

    # Словари маркеров
    DICT_TYPES = {
        '4x4_50': cv2.aruco.DICT_4X4_50,
        '4x4_100': cv2.aruco.DICT_4X4_100,
        '4x4_250': cv2.aruco.DICT_4X4_250,
        '4x4_1000': cv2.aruco.DICT_4X4_1000,
        '5x5_50': cv2.aruco.DICT_5X5_50,
        '5x5_100': cv2.aruco.DICT_5X5_100,
        '5x5_250': cv2.aruco.DICT_5X5_250,
        '5x5_1000': cv2.aruco.DICT_5X5_1000,
        '6x6_50': cv2.aruco.DICT_6X6_50,
        '6x6_100': cv2.aruco.DICT_6X6_100,
        '6x6_250': cv2.aruco.DICT_6X6_250,
        '6x6_1000': cv2.aruco.DICT_6X6_1000,
        '7x7_50': cv2.aruco.DICT_7X7_50,
        '7x7_100': cv2.aruco.DICT_7X7_100,
        '7x7_250': cv2.aruco.DICT_7X7_250,
        '7x7_1000': cv2.aruco.DICT_7X7_1000,
        'aruco_original': cv2.aruco.DICT_ARUCO_ORIGINAL,
        'april_16h5': cv2.aruco.DICT_APRILTAG_16h5,
        'april_25h9': cv2.aruco.DICT_APRILTAG_25h9,
        'april_36h10': cv2.aruco.DICT_APRILTAG_36h10,
        'april_36h11': cv2.aruco.DICT_APRILTAG_36h11,
    }

    def __init__(self,
                 dict_type: str = '6x6_250',
                 marker_size: float = 0.05,
                 camera_matrix: Optional[np.ndarray] = None,
                 dist_coeffs: Optional[np.ndarray] = None,
                 detector_params: Optional[cv2.aruco.DetectorParameters] = None):
        """
        Инициализация детектора ArUco маркеров

        Args:
            dict_type: Тип словаря маркеров
            marker_size: Размер маркера в метрах (для оценки позы)
            camera_matrix: Матрица камеры (3x3)
            dist_coeffs: Коэффициенты дисторсии
            detector_params: Параметры детектора
        """
        self.dict_type = dict_type
        self.marker_size = marker_size

        # Инициализация словаря
        if dict_type not in self.DICT_TYPES:
            raise ValueError(f"Unknown dictionary type: {dict_type}. Available: {list(self.DICT_TYPES.keys())}")

        self.aruco_dict = cv2.aruco.getPredefinedDictionary(self.DICT_TYPES[dict_type])

        # Параметры детектора
        self.detector_params = detector_params or cv2.aruco.DetectorParameters()

        # Создание детектора
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.detector_params)

        # Параметры камеры
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs or np.zeros((5, 1), dtype=np.float32)

        # Хранилище для известных маркеров
        self.known_markers = {}  # {marker_id: {'name': str, 'size': float, 'pose': np.ndarray}}

        # Статистика
        self.detection_stats = {
            'total_frames': 0,
            'detected_frames': 0,
            'total_markers': 0
        }

    def set_camera_params(self,
                          camera_matrix: np.ndarray,
                          dist_coeffs: Optional[np.ndarray] = None):
        """
        Установка параметров камеры

        Args:
            camera_matrix: Матрица камеры 3x3
            dist_coeffs: Коэффициенты дисторсии
        """
        self.camera_matrix = camera_matrix
        if dist_coeffs is not None:
            self.dist_coeffs = dist_coeffs

    def load_camera_params(self, filepath: str):
        """
        Загрузка параметров камеры из файла

        Args:
            filepath: Путь к файлу .npz с параметрами камеры
        """
        data = np.load(filepath)
        self.camera_matrix = data['camera_matrix']
        self.dist_coeffs = data['dist_coeffs']
        print(f"Camera parameters loaded from {filepath}")

    def add_known_marker(self,
                         marker_id: int,
                         name: str,
                         size: Optional[float] = None,
                         pose: Optional[np.ndarray] = None):
        """
        Добавление известного маркера

        Args:
            marker_id: ID маркера
            name: Имя маркера
            size: Размер маркера в метрах (если None, используется общий размер)
            pose: Положение маркера в системе координат (4x4 матрица преобразования)
        """
        self.known_markers[marker_id] = {
            'name': name,
            'size': size or self.marker_size,
            'pose': pose  # Положение маркера в мире
        }

    def detect_markers(self,
                       image: np.ndarray,
                       estimate_pose: bool = False,
                       draw: bool = False) -> Dict:
        """
        Детекция маркеров на изображении

        Args:
            image: Входное изображение (BGR или grayscale)
            estimate_pose: Оценивать позу маркера
            draw: Отрисовывать маркеры на изображении

        Returns:
            Словарь с результатами детекции
        """
        result = {
            'corners': None,
            'ids': None,
            'rvecs': None,
            'tvecs': None,
            'image': image.copy() if draw else None,
            'markers_info': []
        }

        # Конвертация в оттенки серого если нужно
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Детекция маркеров
        corners, ids, rejected = self.detector.detectMarkers(gray)

        if ids is not None:
            result['corners'] = corners
            result['ids'] = ids.flatten()

            # Отрисовка если нужно
            if draw:
                cv2.aruco.drawDetectedMarkers(image, corners, ids)
                result['image'] = image

            # Оценка позы если заданы параметры камеры
            if estimate_pose and self.camera_matrix is not None:
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners, self.marker_size, self.camera_matrix, self.dist_coeffs
                )
                result['rvecs'] = rvecs
                result['tvecs'] = tvecs

                # Отрисовка осей если нужно
                if draw:
                    for i in range(len(ids)):
                        cv2.drawFrameAxes(image, self.camera_matrix, self.dist_coeffs,
                                          rvecs[i], tvecs[i], self.marker_size / 2)

            # Сбор информации о каждом маркере
            for i, marker_id in enumerate(result['ids']):
                marker_info = {
                    'id': int(marker_id),
                    'name': self.known_markers.get(marker_id, {}).get('name', f'Marker_{marker_id}'),
                    'corners': corners[i].tolist() if corners is not None else None,
                    'center': self._get_marker_center(corners[i]) if corners is not None else None
                }

                if estimate_pose and result['rvecs'] is not None:
                    marker_info.update({
                        'rotation': result['rvecs'][i].tolist(),
                        'translation': result['tvecs'][i].tolist(),
                        'distance': self._calculate_distance(result['tvecs'][i])
                    })

                result['markers_info'].append(marker_info)

            # Обновление статистики
            self.detection_stats['total_frames'] += 1
            self.detection_stats['detected_frames'] += 1
            self.detection_stats['total_markers'] += len(ids)

        else:
            self.detection_stats['total_frames'] += 1

        return result

    def _get_marker_center(self, corners: np.ndarray) -> Tuple[float, float]:
        """Вычисление центра маркера"""
        corners = corners.reshape(4, 2)
        center = corners.mean(axis=0)
        return (float(center[0]), float(center[1]))

    def _calculate_distance(self, tvec: np.ndarray) -> float:
        """Вычисление расстояния до маркера"""
        return float(np.linalg.norm(tvec))

    def generate_marker(self,
                        marker_id: int,
                        size_pixels: int = 200,
                        border_bits: int = 1) -> np.ndarray:
        """
        Генерация изображения маркера

        Args:
            marker_id: ID маркера
            size_pixels: Размер изображения в пикселях
            border_bits: Толщина границы в битах

        Returns:
            Изображение маркера
        """
        return cv2.aruco.generateImageMarker(
            self.aruco_dict, marker_id, size_pixels, borderBits=border_bits
        )

    def generate_board(self,
                       markers_x: int = 5,
                       markers_y: int = 7,
                       marker_length: float = 0.04,
                       marker_separation: float = 0.01,
                       image_size: Tuple[int, int] = (600, 500)) -> Tuple[np.ndarray, cv2.aruco.CharucoBoard]:
        """
        Генерация ChArUco доски

        Args:
            markers_x: Количество маркеров по X
            markers_y: Количество маркеров по Y
            marker_length: Длина маркера в метрах
            marker_separation: Расстояние между маркерами в метрах
            image_size: Размер изображения (ширина, высота)

        Returns:
            Изображение доски и объект доски
        """
        board = cv2.aruco.CharucoBoard(
            (markers_x, markers_y),
            marker_length,
            marker_separation,
            self.aruco_dict
        )

        board_image = board.generateImage(image_size)
        return board_image, board

    def detect_charuco_board(self,
                             image: np.ndarray,
                             board: cv2.aruco.CharucoBoard,
                             draw: bool = False) -> Dict:
        """
        Детекция ChArUco доски

        Args:
            image: Входное изображение
            board: Объект ChArUco доски
            draw: Отрисовывать результаты

        Returns:
            Результаты детекции
        """
        result = {
            'charuco_corners': None,
            'charuco_ids': None,
            'marker_corners': None,
            'marker_ids': None,
            'image': image.copy() if draw else None
        }

        detector = cv2.aruco.CharucoDetector(board)
        charuco_corners, charuco_ids, marker_corners, marker_ids = detector.detectBoard(image)

        if charuco_corners is not None and charuco_ids is not None:
            result['charuco_corners'] = charuco_corners
            result['charuco_ids'] = charuco_ids.flatten()
            result['marker_corners'] = marker_corners
            result['marker_ids'] = marker_ids.flatten() if marker_ids is not None else None

            if draw:
                cv2.aruco.drawDetectedCornersCharuco(image, charuco_corners, charuco_ids)

        return result

    def process_video(self,
                      video_source: Union[int, str] = 0,
                      process_callback: Optional[callable] = None,
                      show_video: bool = True,
                      exit_key: str = 'q') -> None:
        """
        Обработка видео в реальном времени

        Args:
            video_source: Источник видео (0 для камеры, или путь к файлу)
            process_callback: Функция обратного вызова для обработки результатов
            show_video: Показывать видео
            exit_key: Клавиша для выхода
        """
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            print(f"Error: Cannot open video source {video_source}")
            return

        print(f"Processing video from {video_source}")
        print(f"Press '{exit_key}' to exit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Детекция маркеров
            result = self.detect_markers(frame, estimate_pose=True, draw=True)

            # Вывод информации о маркерах
            if result['ids'] is not None:
                print(f"\rDetected markers: {len(result['ids'])}", end="")
                for marker_info in result['markers_info']:
                    print(f"\n  {marker_info['name']}: dist={marker_info.get('distance', 0):.2f}m", end="")

            # Вызов callback функции если задана
            if process_callback:
                process_callback(result)

            # Показ видео
            if show_video and result['image'] is not None:
                cv2.imshow('ArUco Detection', result['image'])

            # Выход по клавише
            if cv2.waitKey(1) & 0xFF == ord(exit_key):
                break

        cap.release()
        cv2.destroyAllWindows()
        print(f"\nVideo processing stopped. Statistics: {self.detection_stats}")

    def save_marker_image(self,
                          marker_id: int,
                          output_path: str = None,
                          size_pixels: int = 200):
        """
        Сохранение изображения маркера в файл

        Args:
            marker_id: ID маркера
            output_path: Путь для сохранения
            size_pixels: Размер изображения
        """
        if output_path is None:
            output_path = f"marker_{marker_id}.png"

        marker_image = self.generate_marker(marker_id, size_pixels)
        cv2.imwrite(output_path, marker_image)
        print(f"Marker {marker_id} saved to {output_path}")

    def get_detection_stats(self) -> Dict:
        """Получение статистики детекции"""
        return self.detection_stats.copy()

    def get_detection_rate(self) -> float:
        """Получение процента успешной детекции"""
        if self.detection_stats['total_frames'] == 0:
            return 0.0
        return (self.detection_stats['detected_frames'] / self.detection_stats['total_frames']) * 100

    def reset_stats(self):
        """Сброс статистики"""
        self.detection_stats = {
            'total_frames': 0,
            'detected_frames': 0,
            'total_markers': 0
        }


#if __name__ == "__main__":
    # Создание детектора
    #detector = ArucoMarkerDetector(dict_type='6x6_250', marker_size=0.05)

    # Добавление известных маркеров
    #detector.add_known_marker(0, "Base_Marker")
    #detector.add_known_marker(1, "Robot_Marker")
    #detector.add_known_marker(2, "Target_Marker")

    # Генерация и сохранение маркера
    #detector.save_marker_image(0, "marker_0.png", 300)

    # Пример использования с камерой
    # detector.process_video(0, show_video=True)

    # Пример использования с изображением
    # img = cv2.imread("test_image.jpg")
    # result = detector.detect_markers(img, estimate_pose=False, draw=True)
    # cv2.imshow("Result", result['image'])
    # cv2.waitKey(0)