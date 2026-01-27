import cv2
from Webcam import Webcam
from config import cameras


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
            camera.cap = cap

            cameras.append(camera)
            cap.release()
            camera.is_opened = False

def on_camera_selected(sender, app_data):
    # sender - tag, app_data - str line
    from config import selected_cam, cameras
    index = int(app_data.split()[1])
    selected_cam = (index, cameras[index])