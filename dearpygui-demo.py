import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

dpg.create_context()  # Создание контекста
dpg.create_viewport(title='Custom Title', width=600, height=600) # Создание окна для доступа

demo.show_demo()

dpg.setup_dearpygui()
dpg.show_viewport()  # Показываем окно
dpg.start_dearpygui()  # Запускаем цикл
dpg.destroy_context()  # Уничтожение контекста