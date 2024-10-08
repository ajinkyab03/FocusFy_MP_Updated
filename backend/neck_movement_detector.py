import cv2
import mediapipe as mp
import math

# Initialize MediaPipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Global variables for neck movement detection
prev_neck_position = None
neck_movement_count = 0

def calculate_distance(point1, point2):
    """Calculates the Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def detect_neck_movement(landmarks):
    """Detects neck movement based on the change in neck position."""
    global prev_neck_position, neck_movement_count

    # Neck position can be approximated by averaging shoulder landmarks
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

    # Approximate neck position as the midpoint between the shoulders
    neck_position = [(left_shoulder[0] + right_shoulder[0]) / 2,
                     (left_shoulder[1] + right_shoulder[1]) / 2]

    # Check if there's a previous neck position
    if prev_neck_position is not None:
        # Calculate the movement distance
        movement_distance = calculate_distance(prev_neck_position, neck_position)
        
        # If the neck has moved significantly, increment the neck movement count
        if movement_distance > 0.01:  # Adjust threshold based on sensitivity
            neck_movement_count += 1

    # Update the previous neck position
    prev_neck_position = neck_position

    return neck_movement_count

def generate_frame():
    """Main function to capture frames and detect neck movement."""
    global neck_movement_count

    cap = cv2.VideoCapture(0)  # Open webcam

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB before processing
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image and detect the pose landmarks
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            # Detect neck movements based on the landmarks
            neck_movement_count = detect_neck_movement(results.pose_landmarks.landmark)

            # Visualize the pose landmarks (optional)
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Display the frame with the movement count
        cv2.putText(frame, f'Neck Movements: {neck_movement_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode the frame and yield it
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield frame, neck_movement_count

    cap.release()
