import cv2
import mediapipe as mp
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# COM interface activation
device = AudioUtilities.GetSpeakers()
interface = device._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    model_complexity=0
)

vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

vol_smooth = []
SMOOTH_SIZE = 5
MIN_DIST = 0.1
MAX_DIST = 1.0

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

            wrist_x, wrist_y = landmarks[0][1], landmarks[0][2]
            middle_base_x, middle_base_y = landmarks[9][1], landmarks[9][2]
            hand_size = ((wrist_x - middle_base_x)**2 + (wrist_y - middle_base_y)**2) ** 0.5

            if hand_size == 0:
                continue

            tx, ty = landmarks[4][1], landmarks[4][2]
            ix, iy = landmarks[8][1], landmarks[8][2]
            mx, my = (tx + ix) // 2, (ty + iy) // 2

            raw_distance = ((ix - tx)**2 + (iy - ty)**2) ** 0.5
            distance = raw_distance / hand_size
            distance = np.clip(distance, MIN_DIST, MAX_DIST)

            vol = np.interp(distance, [MIN_DIST, MAX_DIST], [min_vol, max_vol])
            vol_percent = np.interp(distance, [MIN_DIST, MAX_DIST], [0, 100])

            vol_smooth.append(vol)
            if len(vol_smooth) > SMOOTH_SIZE:
                vol_smooth.pop(0)
            smoothed_vol = sum(vol_smooth) / len(vol_smooth)
            volume.SetMasterVolumeLevel(smoothed_vol, None)

            color = (0, 0, 255) if distance < 0.15 else (0, 255, 0)
            cv2.line(frame, (tx, ty), (ix, iy), color, 2)
            cv2.circle(frame, (tx, ty), 8, color, -1)
            cv2.circle(frame, (ix, iy), 8, color, -1)
            cv2.circle(frame, (mx, my), 6, (255, 255, 0), -1)

            if distance < 0.15:
                label = "MIN VOLUME"
                label_color = (0, 0, 255)
            elif distance > 0.85:
                label = "MAX VOLUME"
                label_color = (0, 255, 0)
            else:
                label = f"Volume: {int(vol_percent)}%"
                label_color = (255, 255, 255)

            cv2.putText(frame, label, (mx - 60, my - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, label_color, 2)

            bar_x = 50
            bar_y_top = 150
            bar_y_bottom = 400
            bar_h = int(np.interp(vol_percent, [0, 100], [bar_y_bottom, bar_y_top]))

            cv2.rectangle(frame, (bar_x, bar_y_top), (bar_x + 30, bar_y_bottom), (200, 200, 200), 2)
            cv2.rectangle(frame, (bar_x, bar_h), (bar_x + 30, bar_y_bottom), (0, 255, 0), -1)
            cv2.putText(frame, f"{int(vol_percent)}%", (bar_x - 5, bar_y_bottom + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.putText(frame, "Pinch = min | Open = max volume", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    cv2.imshow("Volume Control", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()