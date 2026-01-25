import cv2
import os


def get_webcams_opencv():
    """Получить список доступных веб-камер через OpenCV"""
    webcams = []

    # Проверяем первые 10 индексов камер (обычно достаточно)
    for index in range(10):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # CAP_DSHOW для Windows
        # Для Linux/Mac: cap = cv2.VideoCapture(index)

        if cap.isOpened():
            # Получаем информацию о камере
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            webcam_info = {
                'index': index,
                'name': f'Камера {index}',
                'resolution': f'{width}x{height}',
                'fps': fps,
                'width': width,
                'height': height,
                'backend': 'OpenCV'
            }
            webcams.append(webcam_info)
            cap.release()

    return webcams


# Использование
cameras = get_webcams_opencv()
print(f"Найдено камер: {len(cameras)}")
for cam in cameras:
    print(f"Индекс: {cam['index']}, Разрешение: {cam['resolution']}, FPS: {cam['fps']}")