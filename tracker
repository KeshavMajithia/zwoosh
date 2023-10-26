import cv2
import mediapipe as mp
import time
import serial

# Initialize serial connection to your Arduino
ser = serial.Serial('COM5', 9600)  # Replace 'COM5' with your Arduino's COM port
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
capture = cv2.VideoCapture(1)
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

# Initialize the secondary camera
cap = cv2.VideoCapture(1)  # Adjust the camera index as needed

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
