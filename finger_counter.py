import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

tip_ids = [4, 8, 12, 16, 20]

def count_fingers(landmarks):
    fingers = []

    # thumb — compare tip with base of pinky for better accuracy
    if abs(landmarks[4][1] - landmarks[9][1]) > 40:
        fingers.append(1)
    else:
        fingers.append(0)

    # other 4 fingers
    for tip in tip_ids[1:]:
        if landmarks[tip][2] < landmarks[tip - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    total_count = 0

    if results.multi_hand_landmarks:
        for i, lm in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            # get hand label (Left or Right)
            hand_label = results.multi_handedness[i].classification[0].label

            h, w, _ = frame.shape
            landmarks = [[id, int(x * w), int(y * h)] for id, (x, y, z) in
                         enumerate([(l.x, l.y, l.z) for l in lm.landmark])]

            fingers = count_fingers(landmarks)
            count = fingers.count(1)
            total_count += count

            # show count above each hand
            x = landmarks[0][1]
            y = landmarks[0][2]
            cv2.putText(frame, f"{hand_label}: {count}", (x - 30, y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.putText(frame, f"Total: {total_count}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow("Finger Counter", frame)
    
    # click on the window first then press Q to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # Q or ESC to quit
        break

cap.release()
cv2.destroyAllWindows()