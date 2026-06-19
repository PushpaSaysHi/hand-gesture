import cv2
import mediapipe as mp
import numpy as np
import screen_brightness_control as sbc
from collections import deque

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    model_complexity=0
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

bright_smooth = deque(maxlen=5)
MIN_DIST = 0.1   # pinched = min brightness
MAX_DIST = 1.0   # open = max brightness

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            landmarks = [[id, int(lx * w), int(ly * h)] for id, (lx, ly, lz) in
                         enumerate([(l.x, l.y, l.z) for l in lm.landmark])]

            # hand size for normalization
            wrist_x, wrist_y = landmarks[0][1], landmarks[0][2]
            mid_x, mid_y = landmarks[9][1], landmarks[9][2]
            hand_size = ((wrist_x - mid_x)**2 + (wrist_y - mid_y)**2) ** 0.5

            if hand_size == 0:
                continue

            # thumb and index fingertips
            tx, ty = landmarks[4][1], landmarks[4][2]
            ix, iy = landmarks[8][1], landmarks[8][2]
            mx, my = (tx + ix) // 2, (ty + iy) // 2

            # normalized distance
            raw_dist = ((ix - tx)**2 + (iy - ty)**2) ** 0.5
            distance = np.clip(raw_dist / hand_size, MIN_DIST, MAX_DIST)

            # map to brightness 0-100
            brightness = int(np.interp(distance, [MIN_DIST, MAX_DIST], [0, 100]))

            # smooth it
            bright_smooth.append(brightness)
            smoothed = int(sum(bright_smooth) / len(bright_smooth))

            # set brightness
            try:
                sbc.set_brightness(smoothed)
            except Exception:
                pass  # some monitors don't support software brightness

            # draw
            color = (0, 0, 255) if distance < 0.15 else (0, 255, 255)
            cv2.line(frame, (tx, ty), (ix, iy), color, 2)
            cv2.circle(frame, (tx, ty), 8, color, -1)
            cv2.circle(frame, (ix, iy), 8, color, -1)
            cv2.circle(frame, (mx, my), 6, (255, 255, 255), -1)

            # label
            if distance < 0.15:
                label = "MIN BRIGHTNESS"
                label_color = (0, 0, 255)
            elif distance > 0.85:
                label = "MAX BRIGHTNESS"
                label_color = (0, 255, 255)
            else:
                label = f"Brightness: {smoothed}%"
                label_color = (255, 255, 255)

            cv2.putText(frame, label, (mx - 80, my - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, label_color, 2)

            # brightness bar on left
            bar_x = 50
            bar_y_top = 150
            bar_y_bottom = 400
            bar_h = int(np.interp(smoothed, [0, 100], [bar_y_bottom, bar_y_top]))

            cv2.rectangle(frame, (bar_x, bar_y_top), (bar_x + 30, bar_y_bottom), (200, 200, 200), 2)
            cv2.rectangle(frame, (bar_x, bar_h), (bar_x + 30, bar_y_bottom), (0, 255, 255), -1)
            cv2.putText(frame, f"{smoothed}%", (bar_x - 5, bar_y_bottom + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.putText(frame, "Pinch = min | Open = max brightness", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    cv2.imshow("Brightness Control", frame)
    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
        break

cap.release()
cv2.destroyAllWindows()