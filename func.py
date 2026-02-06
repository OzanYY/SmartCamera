import math
import socket
import cv2
import datetime
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
        log_message("Camera started")
    else:
        log_message("Camera is not selected", "ERROR")


def on_stop_camera(sender, app_data):
    """Остановка камеры"""
    camera = selected_cam

    if camera is not None:
        if camera.cap is not None:
            camera.cap.release()
            camera.cap = None

        camera.is_opened = False
        dpg.set_value("image_texture", np.zeros((selected_cam.width, selected_cam.height, 3), dtype=np.float32))
        log_message("Camera stopped")
    else:
        log_message("Camera is not selected", "ERROR")


def on_start_scan(sender, app_data):
    global scan_started
    camera = selected_cam
    if camera is not None:
        scan_started = not scan_started
    else:
        log_message("Camera is not selected", "ERROR")


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
            for i in range(len(calibration) - 2):
                color = [255, 0, 0]
                for j in range(len(scan_output['markers_info'])):
                    if point_in_circle(
                            calibration[str(i)]['center'][0],
                            calibration[str(i)]['center'][1],
                            calibration[str(i)]['size'] / 2 * calibration[str(i)]['tolerance'],
                            scan_output['markers_info'][j]['center'][0],
                            scan_output['markers_info'][j]['center'][1]):
                        color = [0, 255, 0]
                        break
                frame_normalized = drawer.draw_circle(
                    calibration[str(i)]['center'][0],
                    calibration[str(i)]['center'][1],
                    calibration[str(i)]['size'] / 2 * calibration[str(i)]['tolerance'],
                    color,
                    thickness=2
                )
                frame_normalized = drawer.draw_text(
                    calibration[str(i)]['center'][0] - calibration[str(i)]['size'] / 2 * calibration[str(i)]['tolerance'],
                    calibration[str(i)]['center'][1] - calibration[str(i)]['size'] / 2 * calibration[str(i)]['tolerance'],
                    calibration[str(i)]['id'],
                    [255, 0, 255],
                    scale=int(2 * calibration[str(i)]['tolerance'])
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
        log_message("Camera is not selected", "ERROR")
        return

    if not camera.is_opened:
        log_message("Camera is not started", "ERROR")
        return

    if not scan_started:
        log_message("Camera is not scanning", "ERROR")
        return

    if not scan_output['markers_info']:
        log_message("Markers are not found", "ERROR")
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
            "tolerance": k,
            "line_attachment": ""
        }
    dpg.configure_item("calibration_info", default_value=f"Calibrated positions: {len(calibration) - 2}")
    update_reassignment_ui()
    update_assignment_ui()
    log_message(calibration)


def on_reset_calibrate(sender, app_data):
    global calibration
    calibration = {}
    dpg.configure_item("calibration_info", default_value=f"Calibrated positions: {len(calibration)}")
    update_reassignment_ui()
    update_assignment_ui()
    log_message("Calibration reset", "SUCCESS")


def on_save_calibration(sender, app_data):
    global calibration
    with open('calibration.json', 'w', encoding='utf-8') as f:
        json.dump(calibration, f, ensure_ascii=False, indent=2)
    log_message("Calibration saved", "SUCCESS")


def on_load_calibration(sender, app_data):
    if scan_started:
        global calibration
        with open('calibration.json', 'r', encoding='utf-8') as f:
            calibration = json.load(f)
        dpg.configure_item("calibration_info", default_value=f"Calibrated positions: {len(calibration) - 2}")
        update_reassignment_ui()
        update_assignment_ui()
        log_message("Calibration loaded", "SUCCESS")
        log_message(calibration)
    else:
        log_message("Camera not scanning", "ERROR")


def on_change_tolerance(sender, app_data):
    global tolerance
    tolerance = round(app_data, 2)


def on_update_tolerance(sender, app_data):
    global tolerance
    global calibration

    if calibration:
        for marker in calibration:
            calibration[marker]['tolerance'] = tolerance
        log_message(calibration)
    else:
        log_message("Calibration not find", "ERROR")


def point_in_circle(cx, cy, r, px, py):
    squared_distance = (px - cx) ** 2 + (py - cy) ** 2
    return squared_distance <= r * r


def update_reassignment_ui():
    """Обновление UI переназначения позиций"""
    if dpg.does_item_exist("reassignment_group"):
        dpg.delete_item("reassignment_group", children_only=True)

        if len(calibration) > 0:
            with dpg.group(parent="reassignment_group"):
                dpg.add_input_int(
                    label="Position 1",
                    tag="reassign_from",
                    default_value=0,
                    width=80,
                    parent="reassignment_group",
                    min_value=0,
                    max_value=len(calibration) - 2,
                )
                dpg.add_input_int(
                    label="Position 2",
                    tag="reassign_to",
                    default_value=0,
                    width=80,
                    parent="reassignment_group",
                    min_value=0,
                    max_value=len(calibration) - 2,
                )
            dpg.add_button(
                label="Swap",
                callback=do_reassignment,
                width=160,
                parent="reassignment_group"
            )
        else:
            dpg.add_text("No calibrated positions to reassign", parent="reassignment_group", color=(150, 150, 150))


def do_reassignment():
    from_ = _find_key(dpg.get_value("reassign_from"))
    to_ = _find_key(dpg.get_value("reassign_to"))
    if from_ is None or to_ is None:
        log_message("Position not found", "WARNING")
        return
    calibration[from_]['id'], calibration[to_]['id'] = calibration[to_]['id'], calibration[from_]['id']
    log_message(f"Swapped {from_} to {to_}", "SUCCESS")


def _find_key(_id):
    for key in calibration:
        if key == "width" or key == "height":
            continue
        if calibration[key]['id'] == str(_id):
            return key
    return None


def update_assignment_ui():
    """Обновление UI привязки позиций"""
    if dpg.does_item_exist("assignment_group"):
        dpg.delete_item("assignment_group", children_only=True)

        if len(calibration) > 0:
            num_positions = len(calibration)

            for line_idx in range(1, 7):
                with dpg.group(horizontal=True, parent="assignment_group"):
                    dpg.add_text(f"L{line_idx}:", color=(255, 200, 100))

                    # Создаем чекбоксы для каждой позиции
                    for pos_idx in sorted(calibration.keys()):
                        if pos_idx == "width" or pos_idx == "height":
                            continue
                        is_assigned = False
                        if calibration[pos_idx]['line_attachment'] != "" and calibration[pos_idx]['line_attachment'] == f"L{line_idx}":
                            is_assigned = True
                        dpg.add_checkbox(
                            tag=f"L{line_idx}-{pos_idx}",
                            label=f"Pos{pos_idx}",
                            default_value=is_assigned,
                            callback=toggle_position_assignment,
                            user_data=(line_idx, pos_idx)
                        )
        else:
            dpg.add_text("No calibrated positions to assign", parent="assignment_group", color=(150, 150, 150))


def toggle_position_assignment(sender, app_data):
    if app_data:
        calibration[f'{sender.split('-')[1]}']['line_attachment'] = sender.split('-')[0]
        log_message(f"Mark №{sender.split('-')[1]} attached to line {sender.split('-')[0]}", "SUCCESS")
    else:
        calibration[f'{sender.split('-')[1]}']['line_attachment'] = ""
        log_message(f"Mark №{sender.split('-')[1]} detached from line {sender.split('-')[0]}", "SUCCESS")


def send_camera_data(ip="228", l1="0", l2="0", l3="0", l4="0", l5="0", l6="0"):
    """Отправка данных по UDP"""
    message = f"C:{ip}:0:{l1}:{l2}:{l3}:{l4}:{l5}:{l6}#"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(message, "utf-8"), (config.UDP_IP, config.UDP_PORT))
        sock.close()
        return True, message
    except Exception as e:
        return False, str(e)


def generate_packet(line):
    array = list()
    for obj in calibration:
        if obj == "width" or obj == "height":
            continue
        if calibration[obj]['line_attachment'] == line:
            array.append(str(get_marker_in_circle(obj))) #Определение метки в окружности

    return ','.join(array) if array else "0"


def get_marker_in_circle(number_circle):
    for i in range(len(scan_output['markers_info'])):
        if point_in_circle(
                calibration[str(_find_key(number_circle))]['center'][0],
                calibration[str(_find_key(number_circle))]['center'][1],
                calibration[str(_find_key(number_circle))]['size'] / 2 * calibration[str(_find_key(number_circle))]['tolerance'],
                scan_output['markers_info'][i]['center'][0],
                scan_output['markers_info'][i]['center'][1]):
            return scan_output['markers_info'][i]['id']
    return 0


def toggle_udp():
    """Переключение UDP отправки"""
    config.udp_enabled = not config.udp_enabled
    if config.udp_enabled:
        dpg.configure_item("udp_btn", label="Stop UDP")
        dpg.configure_item("udp_status", default_value="UDP: Enabled")
        dpg.configure_item("udp_status", color=(100, 255, 100))
    else:
        dpg.configure_item("udp_btn", label="Start UDP")
        dpg.configure_item("udp_status", default_value="UDP: Disabled")
        dpg.configure_item("udp_status", color=(255, 150, 100))


def send_udp_once():
    """Однократная отправка по UDP"""
    if len(calibration) < 1:
        log_message("Status: No calibration data to send", "WARNING")
        return

    success, result = send_camera_data(
        l1=generate_packet("L1"),
        l2=generate_packet("L2"),
        l3=generate_packet("L3"),
        l4=generate_packet("L4"),
        l5=generate_packet("L5"),
        l6=generate_packet("L6")
    )

    if success:
        log_message(f"Status: UDP sent - {result}", "SUCCESS")
        dpg.configure_item("udp_status", default_value=f"UDP: Manual send")
        dpg.configure_item("udp_status", color=(100, 255, 100))
    else:
        log_message(f"Status: UDP error - {result}", "ERROR")
        dpg.configure_item("udp_status", default_value=f"UDP Error: {result}")
        dpg.configure_item("udp_status", color=(255, 100, 100))


def send_udp_data():
    if not config.udp_enabled:
        #log_message("UDP is not started", "ERROR")
        return

    if len(calibration) < 1:
        log_message("Status: No calibration data to send", "ERROR")
        return

    success, result = send_camera_data(
        l1=generate_packet("L1"),
        l2=generate_packet("L2"),
        l3=generate_packet("L3"),
        l4=generate_packet("L4"),
        l5=generate_packet("L5"),
        l6=generate_packet("L6")
    )

    if success:
        log_message(f"Status: UDP sent - {result}", "SUCCESS")
        dpg.configure_item("udp_status", default_value=f"UDP: Auto send")
        dpg.configure_item("udp_status", color=(100, 255, 100))
    else:
        log_message(f"Status: UDP error - {result}", "ERROR")
        dpg.configure_item("udp_status", default_value=f"UDP Error: {result}")
        dpg.configure_item("udp_status", color=(255, 100, 100))


def update_udp_configuration():
    config.UDP_IP = dpg.get_value("udp_ip_input")
    config.UDP_PORT = dpg.get_value("udp_port_input")


def clear_logs():
    """Очистка логов"""
    if dpg.does_item_exist("log_window"):
        dpg.delete_item("log_window", children_only=True)
        log_message("Logs cleared", "INFO")


def log_message(message: str, level: str = "INFO"):
    """Добавление сообщения в лог"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    color_map = {
        "INFO": (255, 255, 255),
        "SUCCESS": (0, 255, 0),
        "WARNING": (255, 255, 0),
        "ERROR": (255, 0, 0)
    }

    if dpg.does_item_exist("log_window"):
        try:
            with dpg.mutex():
                dpg.add_text(
                    f"[{timestamp}] [{level}] {message}",
                    parent="log_window",
                    color=color_map.get(level, (255, 255, 255))
                )
            dpg.set_y_scroll("log_window", dpg.get_y_scroll_max("log_window"))
        except:
            pass


def send_interval(interval, timer, func):
    now = datetime.datetime.now().timestamp()
    if now - timer > interval:
        func()
        return now
    return timer