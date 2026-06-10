import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

# tip ids for each finger
# 4=thumb, 8=index, 12=middle, 16=ring, 20=pinky
tip_ids = [4, 8, 12, 16, 20]

def count_fingers(landmarks):
    fingers = []

    # thumb — compare x position (left/right)
    if landmarks[4][1] > landmarks[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # other 4 fingers — compare y position (up/down)
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

    count = 0

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            landmarks = [[id, int(x * w), int(y * h)] for id, (x, y, z) in
                         enumerate([(l.x, l.y, l.z) for l in lm.landmark])]

            fingers = count_fingers(landmarks)
            count = fingers.count(1)

        cv2.putText(frame, f"Fingers: {count}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow("Finger Counter", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()