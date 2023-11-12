import cv2
import mediapipe as mp
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

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
myPose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Open a connection to the camera (0 represents the default camera)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Try using cv2.CAP_DSHOW
#cap=cv2.flip(cap, 1)

# Set the frame size
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Serial port configuration
ser = serial.Serial('COM11', 9600, timeout=1)

previous_position = None

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

        # Define regions
        region_x = int(0.25 * width)  # 25% of the width for region 1
        region_y = int(0.75 * width)  # 75% of the width for region 2

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
                if position_index != previous_position:
                    if region == 1:
                        ser.write('L'.encode())
                    elif region == 2:
                        ser.write('S'.encode())
                    elif region == 3:
                        ser.write('R'.encode())

                    # Update previous position
                    previous_position = position_index

        # Display the frame with boundaries and position
        cv2.imshow('Divided Frame', frame)

        # Break the loop if 'q' key is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # Send commands to set servo motors to new positions
            ser.write('Q'.encode())
            break

        # Wait for a short time to avoid overwhelming the Arduino
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting program.")

finally:
    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

    # Close the serial port
    ser.close()
