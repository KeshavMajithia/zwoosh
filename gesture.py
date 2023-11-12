import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize variables
quadrant_threshold = 100  # Adjust this threshold for quadrant detection
min_gesture_duration = 0.75  # Minimum duration for recognizing a gesture (in seconds)

# Initialize camera
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use 0 for the default camera (webcam)
if not capture.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Set the frame size
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Get the camera frame width and height
w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize mediapipe Hands and Pose
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

myHands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
myPose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Define the colors for the dividing lines (pink in BGR)
pink_color = (147, 20, 255)

# Initialize state variables
prev_quadrant = None
current_gesture = None
gesture_start_time = None

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils

# Initialize the secondary camera
cap = cv2.VideoCapture(1)  # Adjust the camera index as needed

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

    while capture.isOpened():
        found, img = capture.read()
        if not found:
            print("Error: Could not read a frame from the camera.")
            break

        frame_height, frame_width, _ = img.shape

        # Process the frame
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        foundHands = myHands.process(imgRGB)
        foundPose = myPose.process(imgRGB)

        if foundHands.multi_hand_landmarks:
            for hands in foundHands.multi_hand_landmarks:
                for id, location in enumerate(hands.landmark):
                    h, w, c = img.shape
                    hand_x = int(location.x * w)
                    hand_y = int(location.y * h)

                    if hand_x < w // 2:
                        quadrant = 'a'
                    else:
                        quadrant = 'b'

                    if current_gesture is None:
                        if prev_quadrant is not None and prev_quadrant != quadrant:
                            if gesture_start_time is None:
                                gesture_start_time = time.time()

                            if prev_quadrant == 'a' and quadrant == 'b':
                                pyautogui.press('left')
                                current_gesture = 'left'
                            elif prev_quadrant == 'b' and quadrant == 'a':
                                pyautogui.press('right')
                                current_gesture = 'right'
                    else:
                        current_time = time.time()
                        if current_time - gesture_start_time >= min_gesture_duration:
                            current_gesture = None
                            gesture_start_time = None

                    prev_quadrant = quadrant

                mp.solutions.drawing_utils.draw_landmarks(img, hands, mp_hands.HAND_CONNECTIONS)
                cv2.putText(img, "Quadrant: " + quadrant, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        cv2.imshow("GestureControl", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

capture.release()
cv2.destroyAllWindows()
