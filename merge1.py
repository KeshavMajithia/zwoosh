import cv2
import mediapipe as mp
import pyautogui
import serial
import time

min_gesture_duration = 0.75

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

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
myPose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Open a connection to the camera for pose tracking
cap_pose = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap_pose.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap_pose.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Serial port configuration for servo control
ser = serial.Serial('COM8', 9600, timeout=1)
initialize_servo(ser)

previous_position = None

# Hand gesture recognition
mp_hands = mp.solutions.hands
myHands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

cap_gesture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap_gesture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap_gesture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_quadrant = None
current_gesture = None
gesture_start_time = None

try:
    while True:
        # Pose tracking
        ret_pose, frame_pose = cap_pose.read()

        if not ret_pose:
            print("Error capturing frame for pose tracking.")
            break

        height, width, _ = frame_pose.shape
        # Process the image with MediaPipe Pose
        results = myPose.process(frame_pose)

        # Check if a pose is detected
        if results.pose_landmarks:
            # Get landmarks and determine position
            landmarks = results.pose_landmarks.landmark
            position_index = determine_position(landmarks, width)

            # Display position on the frame
            if position_index is not None:
                region = position_index + 1  # Add 1 to convert to 1-based index
                cv2.putText(frame_pose, f"Region: {region}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

                # Send commands through serial communication based on detected position change
                if position_index != previous_position:
                    if region == 1:
                        ser.write('L'.encode())
                    elif region == 2:
                        ser.write('S'.encode())
                    elif region == 3:
                        ser.write('R'.encode())

                    # Update previous position
                    previous_position = position_index

        # Hand gesture recognition
        found, img = cap_gesture.read()
        if not found:
            print("Error: Could not read a frame for gesture recognition.")
            break

        frame_height, frame_width, _ = img.shape
        # Process the frame for hand gesture recognition
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        foundHands = myHands.process(imgRGB)

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
                                pyautogui.press('right')
                                current_gesture = 'right'
                            elif prev_quadrant == 'b' and quadrant == 'a':
                                pyautogui.press('left')
                                current_gesture = 'left'
                    else:
                        current_time = time.time()
                        if current_time - gesture_start_time >= min_gesture_duration:
                            current_gesture = None
                            gesture_start_time = None

                    prev_quadrant = quadrant

                mp.solutions.drawing_utils.draw_landmarks(img, hands, mp_hands.HAND_CONNECTIONS)
                cv2.putText(img, "Quadrant: " + quadrant, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        # Display windows
        cv2.imshow('Divided Frame', frame_pose)
        cv2.imshow("GestureControl", img)

        # Break the loop if 'q' key is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # Send commands to set servo motors to new positions
            ser.write('Q'.encode())
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting program.")

finally:
    # Release the cameras and close OpenCV windows
    cap_pose.release()
    cap_gesture.release()
    cv2.destroyAllWindows()

    # Close the serial port
    ser.close()
