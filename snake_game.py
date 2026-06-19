import cv2
import mediapipe as mp
import numpy as np
import random
import time

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

CELL = 20
COLS = 640 // CELL
ROWS = 480 // CELL

snake = [(COLS // 2, ROWS // 2)]
direction = (1, 0)
pending_direction = (1, 0)
food = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
score = 0
high_score = 0
game_over = False
last_move = time.time()
SPEED = 0.12

DIR_CONFIRM = 3
dir_buffer = []

def get_direction_from_hand(ix, iy, px, py, hand_size):
    # px, py = palm center (landmark 9) as anchor
    dx = ix - px
    dy = iy - py

    dead = hand_size * 0.3

    if abs(dx) < dead and abs(dy) < dead:
        return None

    if abs(dx) > abs(dy) * 1.2:
        return (1, 0) if dx > 0 else (-1, 0)
    elif abs(dy) > abs(dx) * 1.2:
        return (0, 1) if dy > 0 else (0, -1)

    return None

def spawn_food(snake):
    while True:
        f = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if f not in snake:
            return f

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    frame = (frame * 0.35).astype(np.uint8)

    if results.multi_hand_landmarks and not game_over:
        for lm in results.multi_hand_landmarks:
            landmarks = [[id, int(lx * w), int(ly * h)] for id, (lx, ly, lz) in
                         enumerate([(l.x, l.y, l.z) for l in lm.landmark])]

            # index fingertip
            ix = landmarks[8][1]
            iy = landmarks[8][2]

            # palm center as anchor
            px = landmarks[9][1]
            py = landmarks[9][2]

            # hand size
            wx = landmarks[0][1]
            wy = landmarks[0][2]
            hand_size = ((wx - px)**2 + (wy - py)**2) ** 0.5

            new_dir = get_direction_from_hand(ix, iy, px, py, hand_size)

            if new_dir is not None:
                dir_buffer.append(new_dir)
                if len(dir_buffer) > DIR_CONFIRM:
                    dir_buffer.pop(0)

                if dir_buffer.count(new_dir) >= DIR_CONFIRM:
                    if (new_dir[0] != -direction[0] or new_dir[1] != -direction[1]):
                        pending_direction = new_dir
            else:
                dir_buffer.clear()

            # draw palm center
            cv2.circle(frame, (px, py), 8, (100, 100, 255), -1)
            # draw index fingertip
            cv2.circle(frame, (ix, iy), 12, (0, 255, 255), -1)
            # draw line palm to finger
            cv2.line(frame, (px, py), (ix, iy), (150, 150, 150), 2)

            # show direction arrow above palm
            arrow_map = {(1, 0): ">", (-1, 0): "<", (0, 1): "v", (0, -1): "^"}
            cv2.putText(frame, arrow_map.get(pending_direction, "?"),
                        (px - 10, py - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

    # move snake
    if not game_over and time.time() - last_move > SPEED:
        direction = pending_direction
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if head[0] < 0 or head[0] >= COLS or head[1] < 0 or head[1] >= ROWS:
            game_over = True
        elif head in snake:
            game_over = True
        else:
            snake.insert(0, head)
            if head == food:
                score += 1
                high_score = max(score, high_score)
                food = spawn_food(snake)
                SPEED = max(0.06, SPEED - 0.003)
            else:
                snake.pop()

        last_move = time.time()

    # draw grid
    for x in range(0, w, CELL):
        cv2.line(frame, (x, 0), (x, h), (30, 30, 30), 1)
    for y in range(0, h, CELL):
        cv2.line(frame, (0, y), (w, y), (30, 30, 30), 1)

    # draw food
    fx, fy = food
    cv2.rectangle(frame,
                  (fx * CELL + 2, fy * CELL + 2),
                  (fx * CELL + CELL - 2, fy * CELL + CELL - 2),
                  (0, 0, 255), -1)

    # draw snake
    for i, (sx, sy) in enumerate(snake):
        color = (0, 255, 0) if i == 0 else (0, 200, 0)
        cv2.rectangle(frame,
                      (sx * CELL + 1, sy * CELL + 1),
                      (sx * CELL + CELL - 1, sy * CELL + CELL - 1),
                      color, -1)

    # HUD
    cv2.putText(frame, f"Score: {score}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"Best: {high_score}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(frame, "Point finger from palm center", (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    # game over screen
    if game_over:
        overlay = frame.copy()
        cv2.rectangle(overlay, (w//2 - 160, h//2 - 60),
                      (w//2 + 160, h//2 + 70), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        cv2.putText(frame, "GAME OVER", (w//2 - 110, h//2 - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.putText(frame, f"Score: {score}  Best: {high_score}",
                    (w//2 - 120, h//2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Press R to restart", (w//2 - 100, h//2 + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow("Snake Game - Hand Control", frame)

    key = cv2.waitKey(1) & 0xFF
    if key in [ord('q'), 27]:
        break
    elif key == ord('r') and game_over:
        snake = [(COLS // 2, ROWS // 2)]
        direction = (1, 0)
        pending_direction = (1, 0)
        food = spawn_food(snake)
        score = 0
        game_over = False
        SPEED = 0.12
        dir_buffer.clear()

cap.release()
cv2.destroyAllWindows()