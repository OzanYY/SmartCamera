import dearpygui.dearpygui as dpg
import numpy as np
from config import cameras

WIDTH = 1280
HEIGHT = 720

def run():
    dpg.create_context()  # Создание контекста

    contain()

    dpg.create_viewport(title='Configurator SmartCamera', width=WIDTH, height=HEIGHT, resizable=False)  # Создание окна для доступа

    dpg.setup_dearpygui()
    dpg.show_viewport()  # Показываем окно
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()  # Запускаем цикл
    dpg.destroy_context()  # Уничтожение контекста

def contain():
    from func import on_camera_selected
    with dpg.window(tag="Primary Window", no_resize=True):
        with dpg.tab_bar():
            with dpg.tab(label="Webcam"):
                dpg.add_text("SmartCamera in dev", tag="main_label",color=[0, 255, 255])
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_text("Select web camera:")
                    dpg.add_combo(
                        list(map(lambda x: f"Camera {x.camera_id}", cameras)),
                        tag="select_camera",
                        default_value="",
                        callback=on_camera_selected
                    )
                    if not cameras:
                        dpg.add_text("Camera is not found", color=[255, 255, 0])
                    else:
                        dpg.add_text("Camera: 1280x720 (HD 16:9)", color=[150, 150, 150])
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Start Camera", width=200)
                    dpg.add_button(label="Stop Camera", width=200)
                    dpg.add_button(label="Start Scanning", width=200)
                dpg.add_separator()
                dpg.add_text("")
                with dpg.texture_registry():
                    texture_id = dpg.add_raw_texture(
                        width=640,  # ширина изображения
                        height=480,  # высота изображения
                        default_value=np.zeros((480, 640, 3), dtype=np.float32),  # пустой массив
                        format=dpg.mvFormat_Float_rgb,  # формат RGB
                        tag="image_texture"  # уникальный ID
                    )
                dpg.add_image("image_texture", width=640, height=480)
            with dpg.tab(label="Calibration"):
                # Панель калибровки
                dpg.add_text("Calibration Controls:", color=(255, 200, 100))
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Calibrate",
                        tag="calibrate_btn",
                        width=120,
                        enabled=False
                    )
                    dpg.add_button(
                        label="Clear Calibration",
                        width=120
                    )
                    dpg.add_button(
                        label="Save",
                        width=80
                    )
                    dpg.add_button(
                        label="Load",
                        width=80
                    )

                # Настройка множителя размера области
                with dpg.group(horizontal=True):
                    dpg.add_text("Area size multiplier:")
                    dpg.add_input_float(
                        tag="tolerance_multiplier_input",
                        default_value=123,
                        width=80,
                        step=0.1
                    )
                    dpg.add_button(
                        label="Update",
                        width=80
                    )
                    dpg.add_text("(affects next calibration)", color=(150, 150, 150))

                dpg.add_text("Calibrated positions: 0", tag="calibration_info", color=(150, 255, 150))

                dpg.add_separator()
                dpg.add_image("image_texture", width=640, height=480)
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
