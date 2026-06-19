import cv2
import mediapipe as mp
import numpy as np
import pyautogui
from collections import deque

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

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

# screen size
screen_w, screen_h = pyautogui.size()

# smoothing
smooth_x = deque(maxlen=5)
smooth_y = deque(maxlen=5)

# click state
clicking = False
click_cooldown = 0

# how much of the frame to use as the control zone (margins)
MARGIN = 0.15  # 15% margin on each side

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # draw control zone box
    zone_x1 = int(w * MARGIN)
    zone_y1 = int(h * MARGIN)
    zone_x2 = int(w * (1 - MARGIN))
    zone_y2 = int(h * (1 - MARGIN))
    cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2), (100, 100, 100), 1)

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            landmarks = [[id, int(lx * w), int(ly * h)] for id, (lx, ly, lz) in
                         enumerate([(l.x, l.y, l.z) for l in lm.landmark])]

            # index fingertip for moving
            ix = landmarks[8][1]
            iy = landmarks[8][2]

            # thumb tip for click detection
            tx = landmarks[4][1]
            ty = landmarks[4][2]

            # normalize index finger to control zone
            ix_norm = (ix - zone_x1) / (zone_x2 - zone_x1)
            iy_norm = (iy - zone_y1) / (zone_y2 - zone_y1)
            ix_norm = np.clip(ix_norm, 0, 1)
            iy_norm = np.clip(iy_norm, 0, 1)

            # map to screen
            target_x = int(ix_norm * screen_w)
            target_y = int(iy_norm * screen_h)

            # smooth movement
            smooth_x.append(target_x)
            smooth_y.append(target_y)
            cursor_x = int(sum(smooth_x) / len(smooth_x))
            cursor_y = int(sum(smooth_y) / len(smooth_y))

            pyautogui.moveTo(cursor_x, cursor_y)

            # pinch distance for click (thumb + index)
            pinch_dist = ((ix - tx)**2 + (iy - ty)**2) ** 0.5

            # normalize by hand size
            wrist_x, wrist_y = landmarks[0][1], landmarks[0][2]
            mid_x, mid_y = landmarks[9][1], landmarks[9][2]
            hand_size = ((wrist_x - mid_x)**2 + (wrist_y - mid_y)**2) ** 0.5
            if hand_size > 0:
                pinch_norm = pinch_dist / hand_size
            else:
                pinch_norm = 1.0

            # click on pinch
            if click_cooldown > 0:
                click_cooldown -= 1

            if pinch_norm < 0.2 and not clicking and click_cooldown == 0:
                pyautogui.click()
                clicking = True
                click_cooldown = 20  # prevent double clicks
                cv2.putText(frame, "CLICK!", (ix - 30, iy - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            elif pinch_norm >= 0.2:
                clicking = False

            # draw fingertip
            color = (0, 0, 255) if pinch_norm < 0.2 else (0, 255, 0)
            cv2.circle(frame, (ix, iy), 10, color, -1)
            cv2.circle(frame, (tx, ty), 8, (255, 255, 0), -1)
            cv2.line(frame, (ix, iy), (tx, ty), color, 2)

            # HUD
            cv2.putText(frame, f"Pinch: {pinch_norm:.2f}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Cursor: {cursor_x}, {cursor_y}", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.putText(frame, "Index = move | Pinch = click", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    cv2.imshow("Mouse Control", frame)
    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
        break

cap.release()
cv2.destroyAllWindows()