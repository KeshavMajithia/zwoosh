import cv2
import mediapipe as mp

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

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
cap = cv2.VideoCapture(0)  # Adjust the camera index as needed

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame_height, frame_width, _ = frame.shape

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Process the frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        # Check if pose landmarks were detected
        if results.pose_landmarks is not None:
            # Extract pose landmarks
            landmarks = results.pose_landmarks.landmark

            # Determine human position
            position = determine_position(landmarks, frame_width)

            # Draw dividing lines
            for i in range(1, 5):
                x = frame_width * i // 5
                frame = cv2.line(frame, (x, 0), (x, frame_height), (0, 0, 255), 2)

            # Display labels based on the human's position
            if position:
                cv2.putText(frame, position, (frame_width - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow('Human Position Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'Esc' to exit
            break

cap.release()
cv2.destroyAllWindows()
