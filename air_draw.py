import cv2
import mediapipe as mp
import numpy as np

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

canvas = None
prev_x, prev_y = 0, 0
draw_color = (0, 255, 0)
brush_size = 8
mode = "Draw"
cooldown = 0  # ✅ here at the top

buttons = [
    {"label": "Draw",  "x": 10,  "y": 10, "w": 80, "h": 40, "color": (0, 200, 0)},
    {"label": "Erase", "x": 100, "y": 10, "w": 80, "h": 40, "color": (0, 0, 200)},
    {"label": "Clear", "x": 190, "y": 10, "w": 80, "h": 40, "color": (200, 0, 0)},
    {"label": "Green", "x": 280, "y": 10, "w": 80, "h": 40, "color": (0, 255, 0)},
    {"label": "Red",   "x": 370, "y": 10, "w": 80, "h": 40, "color": (0, 0, 255)},
    {"label": "Blue",  "x": 460, "y": 10, "w": 80, "h": 40, "color": (255, 0, 0)},
]

def draw_buttons(frame, current_mode):
    for btn in buttons:
        x, y, w, h = btn["x"], btn["y"], btn["w"], btn["h"]
        color = btn["color"]
        thickness = -1 if btn["label"] == current_mode else 2
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)
        text_color = (0, 0, 0) if thickness == -1 else (255, 255, 255)
        cv2.putText(frame, btn["label"], (x+8, y+28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

def check_button_click(ix, iy):
    for btn in buttons:
        x, y, w, h = btn["x"], btn["y"], btn["w"], btn["h"]
        if x < ix < x+w and y < iy < y+h:
            return btn["label"]
    return None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            landmarks = [[id, int(lx * w), int(ly * h)] for id, (lx, ly, lz) in
                         enumerate([(l.x, l.y, l.z) for l in lm.landmark])]

            ix = landmarks[8][1]
            iy = landmarks[8][2]

            cv2.circle(frame, (ix, iy), 8, (255, 255, 255), -1)

            clicked = check_button_click(ix, iy)

            if clicked:
                if clicked == "Clear":
                    canvas = np.zeros((h, w, 3), dtype=np.uint8)
                elif clicked == "Green":
                    draw_color = (0, 255, 0)
                elif clicked == "Red":
                    draw_color = (0, 0, 255)
                elif clicked == "Blue":
                    draw_color = (255, 0, 0)
                else:
                    mode = clicked
                prev_x, prev_y = 0, 0
                cooldown = 20  # ✅ wait 20 frames

            elif cooldown > 0:
                cooldown -= 1  # ✅ counting down
                prev_x, prev_y = 0, 0

            else:
                if iy > 60:  # ✅ only below buttons
                    if mode == "Draw":
                        if prev_x == 0 and prev_y == 0:
                            prev_x, prev_y = ix, iy
                        cv2.line(canvas, (prev_x, prev_y), (ix, iy), draw_color, brush_size)
                        prev_x, prev_y = ix, iy

                    elif mode == "Erase":
                        cv2.circle(canvas, (ix, iy), 30, (0, 0, 0), -1)
                        cv2.circle(frame, (ix, iy), 30, (0, 0, 255), 2)
                        prev_x, prev_y = 0, 0
                else:
                    prev_x, prev_y = 0, 0

    else:
        prev_x, prev_y = 0, 0

    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    canvas_fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    combined = cv2.add(frame_bg, canvas_fg)

    draw_buttons(combined, mode)
    cv2.putText(combined, f"Mode: {mode}  Brush: {brush_size}", (10, combined.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Air Draw", combined)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == ord('+'): brush_size = min(brush_size + 2, 30)
    elif key == ord('-'): brush_size = max(brush_size - 2, 2)

cap.release()
cv2.destroyAllWindows()