import cv2
import dearpygui.dearpygui as dpg
import numpy as np
from Webcam import Webcam
from config import cameras, selected_cam


def get_webcams_opencv():
    """Получить список доступных веб-камер через OpenCV"""

    # Проверяем первые 10 индексов камер (обычно достаточно)
    for index in range(10):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # CAP_DSHOW для Windows
        # Для Linux/Mac: cap = cv2.VideoCapture(index)

        if cap.isOpened():
            camera = Webcam()
            # Получаем информацию о камере
            camera.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            camera.f = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            camera.fps = cap.get(cv2.CAP_PROP_FPS)
            camera.camera_id = index
            camera.is_opened = True
            camera.cap = None

            cameras.append(camera)
            cap.release()
            camera.is_opened = False

def on_camera_selected(sender, app_data):
    # sender - tag, app_data - str line
    global selected_cam
    index = int(app_data.split()[1])
    selected_cam = cameras[index]
    dpg.configure_item("Camera status", default_value=f"Camera {index} | {selected_cam.width}x{selected_cam.height}px")
    dpg.configure_item(
        "image_texture",
        width=selected_cam.width,
        height=selected_cam.height
    )
    dpg.configure_item("camera_out", width=selected_cam.width, height=selected_cam.height)

def on_start_camera(sender, app_data):
    """Запуск камеры"""
    camera = selected_cam

    if camera is not None:
        if camera.cap is None:
            camera.cap = cv2.VideoCapture(camera.camera_id)
            camera.cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera.width)
            camera.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera.height)

        camera.is_opened = True
        print("Camera started")
    else:
        print("Camera is not selected")

def on_stop_camera(sender, app_data):
    """Остановка камеры"""
    camera = selected_cam

    if camera is not None:
        if camera.cap is not None:
            camera.cap.release()
            camera.cap = None

        camera.is_opened = False
        print("Camera stopped")
    else:
        print("Camera is not selected")


def update_camera_frame():
    """Обновление кадра камеры в текстуре"""
    camera = selected_cam
    if not camera.is_opened or camera.cap is None:
        return

    # Читаем кадр
    ret, frame = camera.cap.read()
    if not ret:
        return

    # Конвертируем BGR (OpenCV) в RGB (DearPyGui)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Нормализуем значения пикселей (0-255 -> 0.0-1.0)
    frame_normalized = frame_rgb.astype(np.float32) / 255.0

    # Обновляем текстуру
    dpg.set_value("image_texture", frame_normalized)