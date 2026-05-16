import cv2
import numpy as np
import random

cv2.namedWindow("Image", cv2.WINDOW_GUI_NORMAL)
cv2.namedWindow("Mask", cv2.WINDOW_GUI_NORMAL)

position = [0, 0]
clicked = False
colors = []
mystery_seq = None

def on_click(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at {x}, {y}")
        global position, clicked
        position = [x, y]
        clicked = True

cv2.setMouseCallback("Image", on_click)
capture = cv2.VideoCapture(0)

while True:
    ret, frame = capture.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    blurred = cv2.GaussianBlur(frame, (5,5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask_display = np.zeros_like(frame)

    found_objects = []
    for i, (lower, upper) in enumerate(colors):
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.medianBlur(mask, 7)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            obj = max(contours, key=cv2.contourArea)
            if cv2.contourArea(obj) > 200:
                x, y, w, h = cv2.boundingRect(obj)
                cx = x + w // 2
                cy = y + h // 2
                found_objects.append({'id': i, 'x': cx, 'y': cy})

                cv2.drawContours(mask_display, [obj], -1, (255, 255, 255), 2)
                cv2.putText(mask_display, str(i), (cx - 10, cy + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    key = cv2.waitKey(50) & 0xFF
    if key == ord("q"):
        break

    # Сохранение цвета по клику
    if clicked:
        clicked = False
        color = hsv[position[1], position[0]]
        lower = np.clip(color * 0.9, 0, 255).astype("u1")
        upper = np.clip(color * 1.1, 0, 255).astype("u1")
        colors.append((lower, upper))
        print(f"{len(colors)} Цвет сохранён")

    # Сброс всех цветов
    if key == ord("e"):
        colors = []
        mystery_seq = None
        print("Список цветов очищен")

    # Загадываем последовательность
    if key == ord("s") and len(colors) >= 3:
        mystery_seq = list(range(len(colors)))
        random.shuffle(mystery_seq)
        print(f"Загадана последовательность: {mystery_seq}")

    # Отгадываем последовательность
    if key == ord("r"):
        if mystery_seq is None:
            print("Сначала загадайте последовательность (клавиша S)")
        elif len(found_objects) != len(colors):
            print(f"Вижу только {len(found_objects)} шаров из {len(colors)}")
        else:
            answer = found_objects.copy()

            if len(colors) == 3:
                answer.sort(key=lambda obj: obj['x'])
            elif len(colors) == 4:
                answer.sort(key=lambda obj: obj['y'])
                top_row = sorted(answer[:2], key=lambda obj: obj['x'])
                bottom_row = sorted(answer[2:], key=lambda obj: obj['x'])
                answer = top_row + bottom_row

            user_seq = [obj['id'] for obj in answer]
            if user_seq == mystery_seq:
                print("ОТГАДАЛ!")
            else:
                print(f"НЕВЕРНО. Твой порядок: {user_seq}, а надо: {mystery_seq}")

    cv2.imshow("Image", frame)
    cv2.imshow("Mask", mask_display)

capture.release()
cv2.destroyAllWindows()