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

<img width="1274" height="691" alt="main_LqrERtgbNm" src="https://github.com/user-attachments/assets/bdf8dbbd-0994-4074-8991-118d2529f795" />

* Кнопка "Calibrate" автоматически калибруется по меткам, которые находятся в кадре
* Кнопка "Clear Calibration" очищает калибровку
* Кнопка "Save" сохраняет калибровку в JSON файл рядом с exe
* Кнопка "Load" получает сохраненную калибровку из файла JSON и импортирует ее в программу
* Параметр "Area size multiplier" отвечает за множитель области калибровки

<img width="1274" height="317" alt="main_wCici8vM49" src="https://github.com/user-attachments/assets/016a8a32-e420-4695-ab3a-17ee57a53ba1" />

* Область "Position Swap/Reassigment" отвечает за возможность поменять позиции местами. Вводится 1 позиция и 2 позиция, а при нажатии на кнопку "Swap" позиции меняются местами
* Область "Positions Assigment (L1-L6)" ответчает за прикрепление позиций к строкам, которые будут отправляться в ControlCenter


**Вкладка "UDP"**

<img width="1274" height="691" alt="main_Ts0nTHrMUE" src="https://github.com/user-attachments/assets/64a47d09-d8b3-4606-9631-d1cc2e59fa1e" />

* Настройка ip и порта куда будет отправляться udp пакет, по умолчанию отравляется на localhost.
* Кнопка "Update" применяет изменения написанные в настройках айпи и порта
* Поле "IP Webcamera" отвечает за ip адресс смарт камеры, т.к. ее нет то первые 3 бита айпи берется из подсети, а последний 4 бит вводтся относительно настроек ControlCenter
* Поле "delay" отвечает за интервал отправки пакета, по умолчанию раз в секунду
* Кнопка "Send Once", отправляет один раз пакет на ControlCenter
* Кнпока "Start UDP", включает периодическую отправку UDP пакета


**Вкладка "Logs"**

<img width="1274" height="691" alt="main_KKX0oTzWY0" src="https://github.com/user-attachments/assets/ee0f8edf-18a4-4f6d-84ef-0db47329598d" />

На данной вкладке можно отслеживать работу системы, ошибки, предупреждения и просто инофрацию о ее работе

## Как компилировать в .exe
В локальном окружении нужно скачать две библиотеки
```
pip install nuitka
```
```
pip install zstandard
```
  
Далее выполнить след команду
```
python -m nuitka --onefile --windows-icon-from-ico=<path-to_ico> --windows-company-name="KIT" --windows-product-name="SmartCamera" --windows-file-version=<version> --windows-product-version=<version> --windows-console-mode=disable main.py
```
