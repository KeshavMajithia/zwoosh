import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize variables
quadrant_threshold = 100  # Adjust this threshold for quadrant detection
min_gesture_duration = 0.75  # Minimum duration for recognizing a gesture (in seconds)

# Initialize camera
capture = cv2.VideoCapture(1)  # Use 0 for the default camera (webcam)
if not capture.isOpened():
    print("Error: Could not open camera.")
    exit()

    
# Set the frame width and height to 1920x1080 for 1080p resolution
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

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

# Define the colors for the dividing lines (yellow in BGR)
yellow_color = (0, 255, 255)
pink_color = (147, 20, 255)

# Initialize state variables
prev_quadrant = None
current_gesture = None
gesture_start_time = None

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils

# Define a function to check the human's position
def determine_position(landmarks, frame_width):
    if landmarks is not None:
        landmarks_center = sum([lm.x for lm in landmarks]) / len(landmarks)

        divisions = 5  # Divide the frame into 5 sections

        section_width = frame_width // divisions
        position_index = min(int(landmarks_center * divisions), divisions - 1)
        positions = ["zero", "one", "mid", "three", "peak"]

        return positions[position_index]

    return None

# Initialize the secondary camera
cap = cv2.VideoCapture(1)  # Adjust the camera index as needed

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

    while capture.isOpened():
        found, img = capture.read()
        if not found:
            print("Error: Could not read a frame from the camera.")
            break

        frame_height, frame_width, _ = img.shape

        # Flip the frame horizontally for a later selfie-view display
        img = cv2.flip(img, 1)

        # Process the frame
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        foundHands = myHands.process(imgRGB)
        foundPose = myPose.process(imgRGB)

        if foundPose.pose_landmarks:
            pose_landmarks = foundPose.pose_landmarks.landmark

            left_shoulder_landmark = pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder_landmark = pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip_landmark = pose_landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip_landmark = pose_landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

            left_shoulder_x, left_shoulder_y = int(left_shoulder_landmark.x * w), int(left_shoulder_landmark.y * h)
            right_shoulder_x, right_shoulder_y = int(right_shoulder_landmark.x * w), int(right_shoulder_landmark.y * h)
            left_hip_x, left_hip_y = int(left_hip_landmark.x * w), int(left_hip_landmark.y * h)
            right_hip_x, right_hip_y = int(right_hip_landmark.x * w), int(right_hip_landmark.y * h)

            pink_line_x = (left_hip_x + right_hip_x) // 2
            yellow_line_y = (left_shoulder_y + right_shoulder_y) // 2 + 20

            cv2.line(img, (0, yellow_line_y), (w, yellow_line_y), yellow_color, 2)
            cv2.line(img, (pink_line_x, 0), (pink_line_x, h), pink_color, 2)

        if foundHands.multi_hand_landmarks:
            for hands in foundHands.multi_hand_landmarks:
                for id, location in enumerate(hands.landmark):
                    h, w, c = img.shape
                    hand_x = int(location.x * w)
                    hand_y = int(location.y * h)

                    if hand_x < pink_line_x:
                        if hand_y < yellow_line_y:
                            quadrant = 'a'
                        else:
                            quadrant = 'c'
                    else:
                        if hand_y < yellow_line_y:
                            quadrant = 'b'
                        else:
                            quadrant = 'd'

                    if current_gesture is None:
                        if prev_quadrant is not None and prev_quadrant != quadrant:
                            if gesture_start_time is None:
                                gesture_start_time = time.time()

                            if prev_quadrant == 'a' and quadrant == 'b':
                                pyautogui.press('right')
                                current_gesture = 'right'
                            elif prev_quadrant == 'b' and quadrant == 'a':
                                pyautogui.press('left')
                                current_gesture = 'left'
                            elif prev_quadrant == 'c' and quadrant == 'd':
                                pyautogui.press('right')
                                current_gesture = 'right'
                            elif prev_quadrant == 'd' and quadrant == 'c':
                                pyautogui.press('left')
                                current_gesture = 'left'
                            elif prev_quadrant == 'a' and quadrant == 'c':
                                pyautogui.press('up')
                                current_gesture = 'up'
                            elif prev_quadrant == 'c' and quadrant == 'a':
                                pyautogui.press('down')
                                current_gesture = 'down'
                            elif prev_quadrant == 'b' and quadrant == 'd':
                                pyautogui.press('up')
                                current_gesture = 'up'
                            elif prev_quadrant == 'd' and quadrant == 'b':
                                pyautogui.press('down')
                                current_gesture = 'down'
                    else:
                        current_time = time.time()
                        if current_time - gesture_start_time >= min_gesture_duration:
                            current_gesture = None
                            gesture_start_time = None

                    prev_quadrant = quadrant

                mp.solutions.drawing_utils.draw_landmarks(img, hands, mp_hands.HAND_CONNECTIONS)
                cv2.putText(img, str("Quadrant: " + quadrant), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        if foundPose.pose_landmarks:
            landmarks = foundPose.pose_landmarks.landmark
            position = determine_position(landmarks, frame_width)
            for i in range(1, 5):
                x = frame_width * i // 5
                img = cv2.line(img, (x, 0), (x, frame_height), (0, 0, 255), 2)
            if position:
                cv2.putText(img, position, (frame_width - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("GestureControl", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

capture.release()
cv2.destroyAllWindows()
