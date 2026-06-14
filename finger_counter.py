import cv2
import mediapipe as mp
from collections import deque

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

tip_ids = [4, 8, 12, 16, 20]

# keep last 5 gesture results for smoothing
gesture_history = deque(maxlen=5)

def count_fingers(landmarks):
    fingers = []

    if abs(landmarks[4][1] - landmarks[9][1]) > 40:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip in tip_ids[1:]:
        if landmarks[tip][2] < landmarks[tip - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def get_gesture(fingers):
    if fingers == [0, 0, 0, 0, 0]: return "Fist",      (0, 0, 255)
    if fingers == [1, 1, 1, 1, 1]: return "Open Hand",  (0, 255, 0)
    if fingers == [0, 1, 0, 0, 0]: return "Pointing",   (255, 255, 0)
    if fingers == [0, 1, 1, 0, 0]: return "Peace",      (0, 255, 255)
    if fingers == [1, 0, 0, 0, 0]: return "Thumbs Up",  (0, 165, 255)
    if fingers == [0, 0, 0, 0, 1]: return "Pinky",      (255, 0, 255)
    if fingers == [1, 1, 0, 0, 1]: return "Rock On",    (255, 0, 0)
    if fingers == [0, 1, 1, 1, 1]: return "Four",       (255, 165, 0)
    return "Unknown", (200, 200, 200)


def smooth_gesture(gesture):
    gesture_history.append(gesture)
    # return most common gesture in history
    return max(set(gesture_history), key=gesture_history.count)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            landmarks = [[id, int(x * w), int(y * h)] for id, (x, y, z) in
                         enumerate([(l.x, l.y, l.z) for l in lm.landmark])]

            fingers = count_fingers(landmarks)
            gesture, color = get_gesture(fingers)

            # smooth the gesture over last 5 frames
            gesture = smooth_gesture(gesture)
            _, color = get_gesture(fingers)

            cv2.putText(frame, gesture, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

            cv2.putText(frame, f"Fingers: {fingers.count(1)}", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Gesture Recognizer", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()