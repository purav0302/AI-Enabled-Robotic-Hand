
import cv2
import mediapipe as mp
import serial
import time

# Connect to Arduino
arduino = serial.Serial("COM19", 115200, timeout=1)
time.sleep(2)

# Set up hand tracking
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Open webcam
cap = cv2.VideoCapture(0)

# Servo angles for each finger
open_angles = {
    "THUMB": 180,
    "INDEX": 0,
    "MIDDLE": 0,
    "RING": 180,
    "PINKY": 0
}

closed_angles = {
    "THUMB": 0,
    "INDEX": 180,
    "MIDDLE": 180,
    "RING": 0,
    "PINKY": 180
}

last_angles = {}

while cap.isOpened():
    success, frame = cap.read()

    if not success:
        break

    # Flip camera image
    frame = cv2.flip(frame, 1)

    # Convert image for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # Draw all 21 landmarks
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            lm = hand_landmarks.landmark

            # Detect whether each finger is open
            # Compare fingertip with middle finger joint
            finger_states = {
                "INDEX": lm[8].y < lm[6].y,
                "MIDDLE": lm[12].y < lm[10].y,
                "RING": lm[16].y < lm[14].y,
                "PINKY": lm[20].y < lm[18].y
            }

            # Detect thumb using landmark distances
            thumb_tip = lm[4]
            thumb_base = lm[2]
            pinky_base = lm[17]

            tip_distance = (
                (thumb_tip.x - pinky_base.x) ** 2 +
                (thumb_tip.y - pinky_base.y) ** 2
            )

            base_distance = (
                (thumb_base.x - pinky_base.x) ** 2 +
                (thumb_base.y - pinky_base.y) ** 2
            )

            finger_states["THUMB"] = (
                tip_distance > base_distance
            )

            # Send finger commands to Arduino
            for finger, is_open in finger_states.items():

                if is_open:
                    angle = open_angles[finger]
                else:
                    angle = closed_angles[finger]

                # Only send when angle changes
                if last_angles.get(finger) != angle:

                    command = f"{finger}:{angle}\n"
                    arduino.write(command.encode())

                    last_angles[finger] = angle

            # Display finger states
            y = 30

            for finger, is_open in finger_states.items():
                state = "OPEN" if is_open else "CLOSED"

                cv2.putText(
                    frame,
                    f"{finger}: {state}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                y += 30

    cv2.imshow("AI Prosthetic Hand Tracking", frame)

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
arduino.close()
hands.close()
cv2.destroyAllWindows()
