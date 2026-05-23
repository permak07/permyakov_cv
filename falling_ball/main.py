import cv2
import numpy as np
import sys
import os

CAMERA_ID = 0
PROJECTOR_WIDTH = 1920
PROJECTOR_HEIGHT = 1080
BALL_RADIUS_CAM = 20
GRAVITY = 0.8
RESTITUTION = 0.5
LINE_DETECTION_MIN_LEN = 60
LINE_DETECTION_MAX_GAP = 20
CANNY_LOW = 50
CANNY_HIGH = 150
BINARY_THRESH = 120

if os.path.exists('homography.npy'):
    H = np.load('homography.npy')
    H_inv = np.linalg.inv(H)
    print("Гомография загружена")
else:
    print("WARNING: homography.npy не найден, используется единичная матрица")
    H = np.eye(3)
    H_inv = np.eye(3)


def cam_to_proj(pt_cam):
    p = np.array([pt_cam[0], pt_cam[1], 1.0])
    p_proj = H_inv @ p
    return (int(p_proj[0] / p_proj[2]), int(p_proj[1] / p_proj[2]))


def detect_lines(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, BINARY_THRESH, 255, cv2.THRESH_BINARY_INV)
    edges = cv2.Canny(binary, CANNY_LOW, CANNY_HIGH)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30,
                            minLineLength=LINE_DETECTION_MIN_LEN,
                            maxLineGap=LINE_DETECTION_MAX_GAP)
    if lines is None:
        return []
    return [(l[0][0], l[0][1], l[0][2], l[0][3]) for l in lines]


def closest_point_on_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return (x1, y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return (x1 + t * dx, y1 + t * dy)


def handle_collision(ball_pos, ball_vel, ball_r, segments):
    x, y = ball_pos[0], ball_pos[1]
    vx, vy = ball_vel[0], ball_vel[1]

    for (x1, y1, x2, y2) in segments:
        cx, cy = closest_point_on_segment(x, y, x1, y1, x2, y2)
        dist = np.hypot(x - cx, y - cy)
        if dist < ball_r and dist > 0.001:
            nx = (x - cx) / dist
            ny = (y - cy) / dist
            overlap = ball_r - dist
            x += nx * overlap
            y += ny * overlap
            vn = vx * nx + vy * ny
            if vn < 0:
                vx -= (1 + RESTITUTION) * vn * nx
                vy -= (1 + RESTITUTION) * vn * ny

    return [x, y], [vx, vy]


cap = cv2.VideoCapture(CAMERA_ID)
if not cap.isOpened():
    print("Не удалось открыть камеру")
    sys.exit(1)

cv2.namedWindow('Projector', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Projector', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
start_pos_cam = [cam_width // 2, 40]

ball_pos_cam = list(start_pos_cam)
ball_vel_cam = [0.0, 0.0]
running = False
ball_radius = BALL_RADIUS_CAM

print("Управление: ПРОБЕЛ - запустить шарик, ESC - выход")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    segments = detect_lines(frame)

    if running:
        vx = ball_vel_cam[0]
        vy = ball_vel_cam[1]

        vy += GRAVITY

        ball_pos_cam[0] += vx
        ball_pos_cam[1] += vy

        ball_vel_cam[0] = vx
        ball_vel_cam[1] = vy

        ball_pos_cam, ball_vel_cam = handle_collision(
            ball_pos_cam, ball_vel_cam, ball_radius, segments
        )

        if ball_pos_cam[1] > cam_height + ball_radius:
            ball_pos_cam = list(start_pos_cam)
            ball_vel_cam = [0.0, 0.0]
            running = False

    proj_img = np.zeros((PROJECTOR_HEIGHT, PROJECTOR_WIDTH, 3), dtype=np.uint8)
    ball_proj = cam_to_proj(ball_pos_cam)
    scale = PROJECTOR_WIDTH / cam_width
    radius_proj = int(ball_radius * scale)
    cv2.circle(proj_img, ball_proj, radius_proj, (255, 255, 255), -1)

    debug = frame.copy()
    for s in segments:
        cv2.line(debug, (s[0], s[1]), (s[2], s[3]), (0, 255, 0), 2)
    cv2.circle(debug, (int(ball_pos_cam[0]), int(ball_pos_cam[1])),
               ball_radius, (0, 0, 255), 2)
    cv2.imshow('Debug', debug)

    cv2.imshow('Projector', proj_img)

    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break
    elif key == ord(' '):
        if not running:
            running = True
            ball_pos_cam = list(start_pos_cam)
            ball_vel_cam = [0.0, 0.0]

cap.release()
cv2.destroyAllWindows()