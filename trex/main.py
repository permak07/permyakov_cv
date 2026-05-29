import cv2
import numpy as np
import time
import pyautogui
from mss import MSS

pyautogui.PAUSE = 0
sct = MSS()

print("Переключись на окно с игры. Старт через 3 сек...")
time.sleep(3)

# Начальный прыжок для старта игры и небольшая пауза
pyautogui.press('space')
time.sleep(0.3)

# Игровое поле
monitor = {
    "top": 272,
    "left": 575,
    "width": 520,
    "height": 145
}

# Настройки геометрии
DINO_RIGHT = 90

# Адаптивная зона: стартуем с 80, растём до 150 за 60 сек
BASE_ZONE_OFFSET = 12
BASE_ZONE_WIDTH =80
MAX_ZONE_WIDTH = 150    
RAMP_TIME = 60.0

# Вертикальные координаты зон
GROUND_Y1, GROUND_Y2 = 105, 135 # Кактусы
AIR_Y1, AIR_Y2 = 50, 95         # Птицы

# Пороги
GROUND_THRESH = 40
AIR_THRESH = 30

# Переменные времени и состояний
start_time = time.time()
last_jump = 0.0
JUMP_COOLDOWN = 0.06
JUMP_DURATION = 0.60

ducking = False
DUCK_EXTRA_TIME = 0.25
duck_until = 0.0
jump_until = 0.0

while True:
    t0 = time.time()

    img = np.array(sct.grab(monitor))
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

    # Перевод в чёрно-белое
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Адаптация зоны сканирования
    elapsed = time.time() - start_time
    speed_ratio = min(elapsed / RAMP_TIME, 1.0)

    zone_offset = int(BASE_ZONE_OFFSET + 20 * speed_ratio)
    zone_width = int(BASE_ZONE_WIDTH + (MAX_ZONE_WIDTH - BASE_ZONE_WIDTH) * speed_ratio)

    zone_x1 = DINO_RIGHT + zone_offset
    zone_x2 = zone_x1 + zone_width

    # Зоны: кактусы и птицы
    ground_zone = thresh[GROUND_Y1:GROUND_Y2, zone_x1:zone_x2]
    air_zone = thresh[AIR_Y1:AIR_Y2, zone_x1:zone_x2]

    # Кол-во белых пикселей
    ground_pixels = cv2.countNonZero(ground_zone)
    air_pixels = cv2.countNonZero(air_zone)

    now = time.time()
    is_jumping = now < jump_until

    # Проверка объектов
    has_ground = ground_pixels > GROUND_THRESH
    has_air = air_pixels > AIR_THRESH

    is_cactus = has_ground
    is_bird = has_air and not has_ground

    # Если обнаружен кактус и мы на земле -> ПРЫГАЕМ
    if is_cactus and (now - last_jump) > JUMP_COOLDOWN and not is_jumping:
        pyautogui.press('space')
        last_jump = now
        jump_until = now + JUMP_DURATION
        # Если приседали — отменяем приседание
        if ducking:
            pyautogui.keyUp('down')
            ducking = False
            duck_until = 0

    # Если обнаружена птица в воздухе и мы на земле -> ПРИСЕДАЕМ
    elif is_bird and not is_jumping:
        if not ducking:
            pyautogui.keyDown('down')
            ducking = True
        duck_until = now + DUCK_EXTRA_TIME

    # Отпускаем кнопку приседания, если время вышло и птицы больше нет
    if ducking and now > duck_until and not is_bird:
        pyautogui.keyUp('down')
        ducking = False

    # Рисуем рамки зон: зеленая (земля), синяя (воздух)
    cv2.rectangle(img, (zone_x1, GROUND_Y1), (zone_x2, GROUND_Y2), (0, 255, 0), 2)
    cv2.rectangle(img, (zone_x1, AIR_Y1), (zone_x2, AIR_Y2), (255, 0, 0), 2)

    # FPS и ширина зоны
    fps = 1.0 / (time.time() - t0 + 0.001)
    info = f"FPS:{int(fps)} W:{zone_width}"
    cv2.putText(img, info, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    cv2.imshow("Dino", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    # Сброс таймера
    elif key == ord('r'):
        start_time = time.time()
        last_jump = 0.0
        jump_until = 0.0
        if ducking:
            pyautogui.keyUp('down')
            ducking = False
        duck_until = 0.0
        print("Таймер сброшен. Зона вернулась к стартовой.")

cv2.destroyAllWindows()