from gc import callbacks

import dearpygui.dearpygui as dpg
import numpy as np
from config import cameras
import func

WIDTH = 1280
HEIGHT = 720

def run():
    dpg.create_context()  # Создание контекста

    contain()

    dpg.create_viewport(title='Configurator SmartCamera', width=WIDTH, height=HEIGHT, resizable=False)  # Создание окна для доступа

    dpg.setup_dearpygui()
    dpg.show_viewport()  # Показываем окно
    dpg.set_primary_window("Primary Window", True)
    while dpg.is_dearpygui_running():
        func.update_camera_frame()
        # 2. Рендерим интерфейс
        dpg.render_dearpygui_frame()
    #dpg.start_dearpygui()  # Запускаем цикл
    dpg.destroy_context()  # Уничтожение контекста

def contain():
    with dpg.window(tag="Primary Window", no_resize=True):
        with dpg.tab_bar():
            with dpg.tab(label="Webcam"):
                dpg.add_text("SmartCamera in dev",color=[0, 255, 255])
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_text("Web camera:")
                    dpg.add_combo(
                        list(map(lambda x: f"Camera {x.camera_id}", cameras)),
                        tag="select_camera",
                        default_value="",
                        callback=func.on_camera_selected
                    )
                    from config import selected_cam
                    temp_text = "Camera is not found"
                    if selected_cam is not None:
                        if selected_cam.camera_id >= 0:
                            temp_text = f"Camera {selected_cam.camera_id}: {selected_cam.width}x{selected_cam.height}"
                    elif cameras:
                        temp_text = "Select camera"
                    dpg.add_text(temp_text, color=[255, 255, 0], tag="Camera status")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Start Camera", width=200, callback=func.on_start_camera)
                    dpg.add_button(label="Stop Camera", width=200, callback=func.on_stop_camera)
                    dpg.add_button(label="Start/Stop Scanning", width=200, callback=func.on_start_scan)
                dpg.add_separator()
                dpg.add_text("")
                if selected_cam:
                    with dpg.texture_registry():
                        dpg.add_raw_texture(
                            width=selected_cam.width,  # ширина изображения
                            height=selected_cam.height,  # высота изображения
                            default_value=np.zeros((selected_cam.width, selected_cam.height, 3), dtype=np.float32),  # пустой массив
                            format=dpg.mvFormat_Float_rgb,  # формат RGB
                            tag="image_texture"  # уникальный ID
                        )
                else:
                    with dpg.texture_registry():
                        dpg.add_raw_texture(
                            width=640,  # ширина изображения
                            height=480,  # высота изображения
                            default_value=np.zeros((480, 640, 3), dtype=np.float32),  # пустой массив
                            format=dpg.mvFormat_Float_rgb,  # формат RGB
                            tag="image_texture"  # уникальный ID
                        )
                dpg.add_image("image_texture", width=640, height=480, tag="camera_out")
            with dpg.tab(label="Calibration"):
                # Панель калибровки
                dpg.add_text("Calibration Controls:", color=(255, 200, 100))
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Calibrate",
                        tag="calibrate_btn",
                        width=120,
                        callback=func.on_calibrate_btn
                    )
                    dpg.add_button(
                        label="Clear Calibration",
                        width=120,
                        callback=func.on_reset_calibrate
                    )
                    dpg.add_button(
                        label="Save",
                        width=80,
                        callback=func.on_save_calibration
                    )
                    dpg.add_button(
                        label="Load",
                        width=80,
                        callback=func.on_load_calibration
                    )

                # Настройка множителя размера области
                with dpg.group(horizontal=True):
                    dpg.add_text("Area size multiplier:")
                    dpg.add_input_float(
                        tag="tolerance_multiplier_input",
                        default_value=1.0,
                        width=180,
                        step=0.1,
                        callback=func.on_change_tolerance
                    )
                    dpg.add_button(
                        label="Update",
                        width=80,
                        callback=func.on_update_tolerance
                    )

                dpg.add_text("Calibrated positions: 0", tag="calibration_info", color=(150, 255, 150))

                dpg.add_separator()
                dpg.add_image("image_texture", width=640, height=480)

                # Переназначение позиций
                with dpg.collapsing_header(label="Position Swap/Reassignment", default_open=False):
                    dpg.add_text("Swap two calibrated positions:", color=(200, 200, 200))
                    with dpg.group(tag="reassignment_group"):
                        dpg.add_text("No calibrated positions to reassign", color=(150, 150, 150))

                dpg.add_separator()

                # Привязка позиций к линиям
                with dpg.collapsing_header(label="Position Assignment (L0-L6)", default_open=False):
                    dpg.add_text("Assign calibrated positions to lines:", color=(200, 200, 200))
                    with dpg.group(tag="assignment_group"):
                        dpg.add_text("No calibrated positions to assign", color=(150, 150, 150))

                dpg.add_separator()
            with dpg.tab(label="UDP"):
                # UDP настройки
                dpg.add_text("UDP Settings:", color=(100, 255, 255))
                with dpg.group(horizontal=True):
                    dpg.add_text("IP:")
                    dpg.add_input_text(
                        tag="udp_ip_input",
                        default_value="qwe", #UDP_IP,
                        width=120
                    )
                    dpg.add_text("Port:")
                    dpg.add_input_text(
                        tag="udp_port_input",
                        default_value="0,0,0,0",  #str(UDP_PORT),
                        width=80
                    )
                    dpg.add_button(
                        label="Update",
                        width=80
                    )

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Start UDP",
                        tag="udp_btn",
                        width=120
                    )
                    dpg.add_button(
                        label="Send Once",
                        width=120
                    )

                dpg.add_text("UDP: Disabled", tag="udp_status", color=(255, 150, 100))
                dpg.add_separator()

                # Вывод считанных значений
                dpg.add_text("Reading Output (Packet):", color=(100, 255, 200))
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        tag="reading_output",
                        default_value="",
                        width=800,
                        readonly=True
                    )
                    dpg.add_button(label="Copy", width=80)
                dpg.add_text("Format: C:228:0:l0:l1:l2:l3:l4:l5:l6#",
                             color=(150, 150, 150))
                dpg.add_separator()
                dpg.add_image("image_texture", width=640, height=480)
