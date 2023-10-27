import cv2
import mediapipe as mp
import pyautogui
import time
import serial

# Initialize serial connection to your Arduino
ser = serial.Serial('COM11', 9600)  # Replace 'COM11' with your Arduino's COM port
time.sleep(2)  # Allow Arduino to initialize

# Initialize variables
min_gesture_duration = 0.75
position = 3  # Default position is "mid"

# Function to update the position based on landmarks
def determine_position(landmarks, frame_width):
    if landmarks is not None:
        landmarks_center = sum([lm.x for lm in landmarks]) / len(landmarks)

        divisions = 5

        section_width = frame_width // divisions
        position_index = min(int(landmarks_center * divisions), divisions - 1)
        return position_index

    return None

# Initialize camera
capture = cv2.VideoCapture(0)
if not capture.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Set the frame width and height to 1920x1080 for 1080p resolution
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Initialize mediapipe Pose
mp_pose = mp.solutions.pose

myPose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Initialize mediapipe Hands from the second code
mp_hands = mp.solutions.hands

myHands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Initialize the secondary camera
cap = cv2.VideoCapture(1)  # Adjust the camera index as needed

# Define the color for the dividing line (pink in BGR)
pink_color = (147, 20, 255)

# Initialize state variables from the second code
prev_quadrant = None
current_gesture = None
gesture_start_time = None

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

    while capture.isOpened():
        found, img = capture.read()
        if not found:
            print("Error: Could not read a frame from the camera.")
            break

        frame_height, frame_width, _ = img.shape
        img = cv2.flip(img, 1)

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        foundPose = myPose.process(imgRGB)

        if foundPose.pose_landmarks:
            landmarks = foundPose.pose_landmarks.landmark
            position_index = determine_position(landmarks, frame_width)

            if position_index is not None:
                position = position_index + 1  # Add 1 to convert to 1-based index

            # Calculate the midpoint between the shoulders (pink line position)
            left_shoulder_x = int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame_width)
            right_shoulder_x = int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame_width)
            pink_line_x = (left_shoulder_x + right_shoulder_x) // 2

        # Send commands to the Arduino based on the current position
        if position == 1:
            ser.write('1'.encode())
        elif position == 2:
            ser.write('2'.encode())
        elif position == 3:
            ser.write('3'.encode())
        elif position == 4:
            ser.write('4'.encode())
        elif position == 5:
            ser.write('5'.encode())

        # Detect hand gestures and perform actions based on the second code
        foundHands = myHands.process(imgRGB)
        if foundHands.multi_hand_landmarks:
            for hands in foundHands.multi_hand_landmarks:
                for id, location in enumerate(hands.landmark):
                    h, w, c = img.shape
                    hand_x = int(location.x * w)
                    hand_y = int(location.y * h)

                    # Determine the quadrant of the hand
                    if hand_x < pink_line_x:
                        quadrant = 'a'
                    else:
                        quadrant = 'b'

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
                    else:
                        # Check if the gesture duration is met
                        current_time = time.time()
                        if current_time - gesture_start_time >= min_gesture_duration:
                            current_gesture = None
                            gesture_start_time = None
                    prev_quadrant = quadrant

                mp.solutions.drawing_utils.draw_landmarks(img, hands, mp_hands.HAND_CONNECTIONS)  # Draw landmarks on hand
                cv2.putText(img, str("Quadrant: " + quadrant), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)  # Display the current quadrant

        # Display the current position on the frame
        if position == 3:
            cv2.putText(img, "mid", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
        else:
            cv2.putText(img, str(position), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        cv2.imshow("GestureControl", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Close the serial connection
ser.close()

capture.release()
cv2.destroyAllWindows()
