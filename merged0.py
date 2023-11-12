import cv2
import mediapipe as mp
import pyautogui
import serial
import time

# Function to initialize servo motors
def initialize_servo(ser):
    # Send commands to set initial positions
    ser.write('I'.encode())
    time.sleep(1)  # Adjust delay as needed

# Function to update the position based on landmarks
def determine_position(landmarks, frame_width):
    if landmarks is not None:
        landmarks_center = sum([lm.x for lm in landmarks]) / len(landmarks)
        divisions = 3  # Updated to 3 since there are three regions
        position_index = min(int(landmarks_center * divisions), divisions - 1)
        return position_index
    return None

# Initialize variables
quadrant_threshold = 100  # Adjust this threshold for quadrant detection
min_gesture_duration = 0.75  # Minimum duration for recognizing a gesture (in seconds)

# Initialize camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use 0 for the default camera (webcam)
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# Set the frame size
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Serial port configuration
ser = serial.Serial('COM11', 9600, timeout=1)

# Get the camera frame width and height
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

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

# Define regions
region_x = int(0.25 * w)  # 25% of the width for region 1
region_y = int(0.75 * w)  # 75% of the width for region 2

try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if the frame was successfully captured
        if not ret:
            print("Error capturing frame. Trying to reconnect...")
            cap.release()
            cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            time.sleep(1)
            continue

        # Get frame dimensions
        height, width, _ = frame.shape

        # Draw boundaries between regions
        frame[:, region_x - 2:region_x + 2, :] = [0, 0, 255]  # Red line for the left boundary
        frame[:, region_y - 2:region_y + 2, :] = [0, 0, 255]  # Red line for the right boundary

        # Process the image with MediaPipe Pose
        results = myPose.process(frame)

        # Check if a pose is detected
        if results.pose_landmarks:
            # Get landmarks and determine position
            landmarks = results.pose_landmarks.landmark
            position_index = determine_position(landmarks, width)

            # Display position on the frame
            if position_index is not None:
                region = position_index + 1  # Add 1 to convert to 1-based index
                cv2.putText(frame, f"Region: {region}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

                # Send commands through serial communication based on detected position change
                if position_index != prev_quadrant:
                    if region == 1:
                        ser.write('L'.encode())
                    elif region == 2:
                        ser.write('S'.encode())
                    elif region == 3:
                        ser.write('R'.encode())

                    # Update previous position
                    prev_quadrant = position_index

        # Process the frame with MediaPipe Hands
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        foundHands = myHands.process(imgRGB)

        if foundHands.multi_hand_landmarks:
            for hands in foundHands.multi_hand_landmarks:
                for id, location in enumerate(hands.landmark):
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

                mp.solutions.drawing_utils.draw_landmarks(frame, hands, mp_hands.HAND_CONNECTIONS)
                cv2.putText(frame, "Quadrant: " + quadrant, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        # Display the frame with boundaries and position
        cv2.imshow('Combined Frame', frame)

        # Break the loop if 'q' key is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # Send commands to set servo motors to new positions
            ser.write('Q'.encode())
            break

        # Wait for a short time to avoid overwhelming the Arduino
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nExiting program.")

finally:
    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

    # Close the serial port
    ser.close()
