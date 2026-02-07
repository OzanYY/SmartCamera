# SmartCamera

**SmarCamera** это программа для эмуляции работы смарт камеры для чемпионата профессионального мастерства в компетенции "Интернет вещей", используя обычную веб камеру.

Программа используют веб камеру, подключенную к компьютеру, ищет на полученном изображении Аруко маркеры, а после отправляет их расположение через UDP в специальную программу - ControlCenter.

## Tech stack

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

[![OpenCV](https://img.shields.io/badge/OpenCV-4.13-5C3EE8?logo=opencv&logoColor=white)](https://github.com/opencv/opencv-python)
[![DearPyGui](https://img.shields.io/badge/Dear%20PyGui-2.1-FF6B6B?)](https://github.com/hoffstadt/DearPyGui)
[![NumPy](https://img.shields.io/badge/NumPy-2.4-013243?logo=numpy&logoColor=white)](https://github.com/numpy/numpy)

## Installation
Просто скачайте .exe файл из последнего релиза

## Use
**Вкладка "Webcam":**

На данной владке можно выбрать веб камеру, которая подключена к компьютеру. Запустить ее, выключить ее и начать сканирование на наличие аруко меток в кадре.

![start camera](https://github.com/user-attachments/assets/e23f6a6d-7091-4853-9add-0f06c330a200)


**Вкладка "Calibration"**

![Описание гифки](https://drive.usercontent.google.com/download?id=1Z8Xzl5BdDk8BNog4FbEja4xwT3rwGPHF&export=view&authuser=0)

**Вкладка "UDP"**


**Вкладка "Logs"**

На данной вкладке можно отслеживать работу системы, ошибки, предупреждения и просто инофрацию о ее работе

## Как компилировать в .exe
В локальном окружении нужно скачать две библиотеки
- pip install nuitka
- pip install zstandard
  
Далее выполнить след команду

python -m nuitka --onefile --windows-icon-from-ico=<path-to_ico> --windows-company-name="KIT" --windows-product-name="SmartCamera" --windows-file-version=<version> --windows-product-version=<version> --windows-console-mode=disable main.py
