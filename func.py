import math
import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import json
import Aruco
import TextureDrawer
from Webcam import Webcam
import config


cameras = config.cameras
selected_cam = config.selected_cam
camera_selected = config.camera_selected
scan_started = config.scan_started
calibration = config.calibration
tolerance = config.tolerance
scan_output = dict()


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
    global camera_selected
    camera_selected = True
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
            camera.cap = cv2.VideoCapture(camera.camera_id, cv2.CAP_DSHOW)
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
        dpg.set_value("image_texture", np.zeros((selected_cam.width, selected_cam.height, 3), dtype=np.float32))
        print("Camera stopped")
    else:
        print("Camera is not selected")


def on_start_scan(sender, app_data):
    global scan_started
    camera = selected_cam
    if camera is not None:
        scan_started = not scan_started
    else:
        print("Camera is not selected")


def update_camera_frame():
    """Обновление кадра камеры в текстуре"""
    camera = selected_cam
    global camera_selected
    global scan_started
    global scan_output
    global calibration

    if camera_selected:
        if not camera.is_opened or camera.cap is None:
            return

        # Читаем кадр
        ret, frame = camera.cap.read()
        if not ret:
            return

        if scan_started:
            det = Aruco.ArucoMarkerDetector(dict_type="aruco_original")
            result = det.detect_markers(frame, estimate_pose=True, draw=True)
            scan_output = result
            frame_rgb = cv2.cvtColor(result['image'], cv2.COLOR_BGR2RGB)
        else:
            # Конвертируем BGR (OpenCV) в RGB (DearPyGui)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Нормализуем значения пикселей (0-255 -> 0.0-1.0)
        frame_normalized = frame_rgb.astype(np.float32) / 255.0

        if calibration:
            drawer = TextureDrawer.TextureDrawer(frame_normalized)
            for i, key in enumerate(calibration):
                if i < 2:
                    continue
                frame_normalized = drawer.draw_circle(
                    calibration[key]['center'][0],
                    calibration[key]['center'][1],
                    calibration[key]['size'] / 2 * calibration[key]['tolerance'], 
                    [255, 0, 0],
                    thickness=2
                )

        # Обновляем текстуру
        dpg.set_value("image_texture", frame_normalized)


def on_calibrate_btn(sender, app_data):
    def find_length(start: list, end: list):
        return math.sqrt(abs(end[0] - start[0]) ** 2 + abs(end[1] - start[1]) ** 2)

    global camera_selected
    global scan_started
    global scan_output
    global calibration
    camera = selected_cam
    k = tolerance

    if camera is None:
        print("Camera is not selected")
        return

    if not camera.is_opened:
        print("Camera is not started")
        return

    if not scan_started:
        print("Camera is not scanning")
        return

    if not scan_output['markers_info']:
        print("Markers are not found")
        return

    # Основная логика
    calibration['width'] = camera.width
    calibration['height'] = camera.height
    for i, marker in enumerate(scan_output['markers_info']):
        calibration[str(i)] = {
            "center": marker['center'],
            "id": str(i),
            "size": round(math.sqrt(
                find_length(marker['corners'][0][0], marker['corners'][0][1]) ** 2 +
                find_length(marker['corners'][0][1], marker['corners'][0][2]) ** 2
            )),
            "tolerance": k
        }
    dpg.configure_item("calibration_info", default_value=f"Calibrated positions: {len(calibration)}")
    print(calibration)


def on_reset_calibrate(sender, app_data):
    global calibration
    calibration = {}
    dpg.configure_item("calibration_info", default_value=f"Calibrated positions: {len(calibration)}")


def on_save_calibration(sender, app_data):
    global calibration
    with open('calibration.json', 'w', encoding='utf-8') as f:
        json.dump(calibration, f, ensure_ascii=False, indent=2)
    print("Calibration saved")


def on_load_calibration(sender, app_data):
    global calibration
    with open('calibration.json', 'r', encoding='utf-8') as f:
        calibration = json.load(f)
    dpg.configure_item("calibration_info", default_value=f"Calibrated positions: {len(calibration)}")
    print("Calibration loaded")
    print(calibration)


def on_change_tolerance(sender, app_data):
    global tolerance
    tolerance = round(app_data, 2)


def on_update_tolerance(sender, app_data):
    global tolerance
    global calibration

    if calibration:
        for marker in calibration:
            calibration[marker]['tolerance'] = tolerance
        print(calibration)
    else:
        print("Calibration not find")
