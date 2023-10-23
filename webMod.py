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

while True:
    found, img = capture.read()
    
    if not found:
        print("Error: Could not read a frame from the camera.")
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    foundHands = myHands.process(imgRGB)
    foundPose = myPose.process(imgRGB)

    # Get the landmarks of the body
    if foundPose.pose_landmarks:
        pose_landmarks = foundPose.pose_landmarks.landmark

        # Calculate the center of the body
        left_shoulder_landmark = pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder_landmark = pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip_landmark = pose_landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip_landmark = pose_landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

        left_shoulder_x, left_shoulder_y = int(left_shoulder_landmark.x * w), int(left_shoulder_landmark.y * h)
        right_shoulder_x, right_shoulder_y = int(right_shoulder_landmark.x * w), int(right_shoulder_landmark.y * h)
        left_hip_x, left_hip_y = int(left_hip_landmark.x * w), int(left_hip_landmark.y * h)
        right_hip_x, right_hip_y = int(right_hip_landmark.x * w), int(right_hip_landmark.y * h)

        # Calculate the midpoint between the hips (pink line position)
        pink_line_x = (left_hip_x + right_hip_x) // 2

        # Calculate the midpoint between the shoulders (yellow line position)
        yellow_line_y = (left_shoulder_y + right_shoulder_y) // 2 + 20  # Move it down by 20 pixels

        # Draw a horizontal yellow line dividing the body into top and bottom
        cv2.line(img, (0, yellow_line_y), (w, yellow_line_y), yellow_color, 2)

        # Draw a vertical pink line dividing the body into left and right
        cv2.line(img, (pink_line_x, 0), (pink_line_x, h), pink_color, 2)

    if foundHands.multi_hand_landmarks:
        for hands in foundHands.multi_hand_landmarks:
            for id, location in enumerate(hands.landmark):
                h, w, c = img.shape
                hand_x = int(location.x * w)
                hand_y = int(location.y * h)

                # Determine the quadrant of the hand
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
                    # Only react to a new gesture if no gesture is currently in progress
                    if prev_quadrant is not None and prev_quadrant != quadrant:
                        if gesture_start_time is None:
                            # Start measuring gesture duration
                            gesture_start_time = time.time()

                        # Check for quadrant transitions and perform key presses
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
                    # Check if the gesture duration is met
                    current_time = time.time()
                    if current_time - gesture_start_time >= min_gesture_duration:
                        current_gesture = None
                        gesture_start_time = None

                prev_quadrant = quadrant

            mp.solutions.drawing_utils.draw_landmarks(img, hands, mp_hands.HAND_CONNECTIONS)  # Draw landmarks on hand
            cv2.putText(img, str("Quadrant: " + quadrant), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 1)  # Display the current quadrant

    cv2.imshow("GestureControl", img)  # Show camera

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit program if the user presses q
        break

capture.release()
cv2.destroyAllWindows()