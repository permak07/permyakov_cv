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

# Настройки геометрии зон обнаружения препятствий
DINO_RIGHT = 90       # Правая граница динозаврика внутри кадра
ZONE_OFFSET = 15      # Дистанция от динозавра до начала зоны сканирования
ZONE_WIDTH = 100      # Ширина зоны сканирования

# считаем итоговые X-координаты зоны сканирования
ZONE_X1 = DINO_RIGHT + ZONE_OFFSET
ZONE_X2 = ZONE_X1 + ZONE_WIDTH

# Вертикальные координаты зон (высота)
GROUND_Y1, GROUND_Y2 = 105, 135  # Кактусы
AIR_Y1, AIR_Y2 = 50, 95         # Птицы

# Пороги кактусов и птиц
GROUND_THRESH = 40
AIR_THRESH = 30

# Переменные для контроля времени и состояний клавиш
last_jump = 0.0
JUMP_COOLDOWN = 0.08    # Минимальный перерыв между прыжками
ducking = False         # ПРиседание
DUCK_EXTRA_TIME = 0.12  # Сколько времени удерживать кнопку приседания
duck_until = 0.0

while True:
    t0 = time.time()

    img = np.array(sct.grab(monitor))
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    
    # Перевод в чёрно-белое
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Зоны: кактусы и птицы
    ground_zone = thresh[GROUND_Y1:GROUND_Y2, ZONE_X1:ZONE_X2]
    air_zone = thresh[AIR_Y1:AIR_Y2, ZONE_X1:ZONE_X2]
    
    # Кол-во белых пикселей в каждой зоне
    ground_pixels = cv2.countNonZero(ground_zone)
    air_pixels = cv2.countNonZero(air_zone)
    
    now = time.time()
    
    # Проверяем, превышен ли порог обнаружения объектов
    has_ground = ground_pixels > GROUND_THRESH
    has_air = air_pixels > AIR_THRESH
    
    # Проверка на кактус
    is_cactus = has_ground
    # Проверка на птицу
    is_bird = has_air and not has_ground

    # Если обнаружен кактус и прошло время прыжка -> ПРЫГАЕМ
    if is_cactus and (now - last_jump) > JUMP_COOLDOWN:
        pyautogui.press('space')
        last_jump = now
        # Если мы в это время приседали — отменяем приседание
        if ducking:
            pyautogui.keyUp('down')
            ducking = False
            duck_until = 0
            
    # Если обнаружена птица в воздухе -> ПРИСЕДАЕМ
    elif is_bird:
        if not ducking:
            pyautogui.keyDown('down')
            ducking = True
        duck_until = now + DUCK_EXTRA_TIME  # Продлеваем время приседания

    # Отпускаем кнопку приседания, если время вышло и птицы больше нет
    if ducking and now > duck_until and not is_bird:
        pyautogui.keyUp('down')
        ducking = False

    
    # Рисуем рамки зон: зеленая (земля), синяя (воздух)
    cv2.rectangle(img, (ZONE_X1, GROUND_Y1), (ZONE_X2, GROUND_Y2), (0, 255, 0), 2)
    cv2.rectangle(img, (ZONE_X1, AIR_Y1), (ZONE_X2, AIR_Y2), (255, 0, 0), 2)
        
    # FPS
    fps = 1.0 / (time.time() - t0 + 0.001)
    cv2.putText(img, f"FPS:{int(fps)}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    

    cv2.imshow("Dino", img)
    
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()