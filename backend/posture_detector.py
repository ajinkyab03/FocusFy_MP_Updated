# import cv2
# import mediapipe as mp
# import base64
# import numpy as np
# import time
# from playsound import playsound
# import os
# from collections import deque

# # Mediapipe initialization
# mp_pose = mp.solutions.pose
# mp_face_mesh = mp.solutions.face_mesh
# mp_drawing = mp.solutions.drawing_utils
# pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
# face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# # Initialize variables for blink detection
# previous_blink_state = False
# blink_count = 0
# blink_history = []
# blink_smooth_window = deque(maxlen=5)  # Moving average for blink detection

# # Variables for angle-based posture detection and calibration
# is_calibrated = False
# calibration_frames = 0
# calibration_shoulder_angles = []
# calibration_neck_angles = []
# shoulder_threshold = None
# neck_threshold = None
# posture_smooth_window = deque(maxlen=5)  # Moving average for posture detection
# last_alert_time = time.time()
# alert_cooldown = 10  # seconds
# sound_file = "alert_sound.mp3"  # Path to your sound file

# # Increase the number of frames for calibration to increase stability
# calibration_frames_target = 50  # Increase calibration frames from 30 to 50

# # Function to calculate the angle between three points
# def calculate_angle(point1, point2, point3):
#     a = np.array(point1)
#     b = np.array(point2)
#     c = np.array(point3)
    
#     ba = a - b
#     bc = c - b
    
#     cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#     angle = np.degrees(np.arccos(cosine_angle))
    
#     return angle

# # Function to draw angles on the frame
# def draw_angle(frame, point1, point2, point3, angle, color):
#     cv2.putText(frame, str(int(angle)), 
#                 tuple(np.add(point2, (10, -10)).astype(int)),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

# # Function to analyze posture based on angles with smoothing
# def analyze_posture(frame, landmarks):
#     global is_calibrated, calibration_frames, shoulder_threshold, neck_threshold, last_alert_time
    
#     # Extract key landmarks
#     left_shoulder = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]),
#                      int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0]))
#     right_shoulder = (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame.shape[1]),
#                       int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame.shape[0]))
#     left_ear = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR].x * frame.shape[1]),
#                 int(landmarks[mp_pose.PoseLandmark.LEFT_EAR].y * frame.shape[0]))

#     # Calculate shoulder and neck angles
#     shoulder_angle = calculate_angle(left_shoulder, right_shoulder, (right_shoulder[0], 0))
#     neck_angle = calculate_angle(left_ear, left_shoulder, (left_shoulder[0], 0))

#     # Calibration process
#     if not is_calibrated and calibration_frames < calibration_frames_target:
#         calibration_shoulder_angles.append(shoulder_angle)
#         calibration_neck_angles.append(neck_angle)
#         calibration_frames += 1
#         return f"Calibrating... {calibration_frames}/{calibration_frames_target}", (255, 255, 0)
    
#     if not is_calibrated:
#         shoulder_threshold = np.mean(calibration_shoulder_angles) - 10
#         neck_threshold = np.mean(calibration_neck_angles) - 10
#         is_calibrated = True
#         print(f"Calibration complete. Shoulder threshold: {shoulder_threshold:.1f}, Neck threshold: {neck_threshold:.1f}")

#     # Add angles to smoothing window
#     posture_smooth_window.append((shoulder_angle, neck_angle))

#     # Apply moving average
#     smooth_shoulder_angle = np.mean([angle[0] for angle in posture_smooth_window])
#     smooth_neck_angle = np.mean([angle[1] for angle in posture_smooth_window])

#     # Posture status check
#     current_time = time.time()
#     if smooth_shoulder_angle < shoulder_threshold or smooth_neck_angle < neck_threshold:
#         if current_time - last_alert_time > alert_cooldown:
#             print("Poor posture detected! Please sit up straight.")
#             if os.path.exists(sound_file):
#                 playsound(sound_file)
#             last_alert_time = current_time
#         return "Poor Posture", (0, 0, 255)  # Red for bad posture
#     else:
#         return "Good Posture", (0, 255, 0)  # Green for good posture

# # Function to analyze focus (blink detection) with smoothing
# def analyze_focus(frame):
#     global previous_blink_state, blink_count, blink_history
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     result = face_mesh.process(rgb_frame)

#     if result.multi_face_landmarks:
#         for face_landmarks in result.multi_face_landmarks:
#             left_eye_top = face_landmarks.landmark[159]
#             left_eye_bottom = face_landmarks.landmark[145]
#             right_eye_top = face_landmarks.landmark[386]
#             right_eye_bottom = face_landmarks.landmark[374]

#             left_eye_distance = abs(left_eye_top.y - left_eye_bottom.y)
#             right_eye_distance = abs(right_eye_top.y - right_eye_bottom.y)
#             eye_open_threshold = 0.02  # Adjust threshold for blinking detection

#             # Average both eyes for more precise blink detection
#             avg_eye_distance = (left_eye_distance + right_eye_distance) / 2

#             # Apply moving average to smooth the blink detection
#             blink_smooth_window.append(avg_eye_distance)
#             smooth_eye_distance = np.mean(blink_smooth_window)

#             # Check for blink
#             if smooth_eye_distance < eye_open_threshold:
#                 if not previous_blink_state:  # Blink detected
#                     blink_count += 1
#                     previous_blink_state = True
#                     blink_history.append(time.time())  # Log blink time
#             else:
#                 previous_blink_state = False  # Reset blink state when eyes are open

#     # Keep only blinks from the last minute
#     blink_history = [t for t in blink_history if time.time() - t < 60]

#     return len(blink_history)

# # Function to generate video frames with posture and blink analysis
# def generate_frame():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("Error: Camera could not be opened.")
#         return

#     global blink_count  # Use global blink_count to keep track
#     blink_count = 0

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             print("Error: Failed to capture frame.")
#             break

#         # Convert frame to RGB for pose detection
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = pose.process(rgb_frame)

#         if results.pose_landmarks:
#             landmarks = results.pose_landmarks.landmark

#             # Analyze posture
#             posture_status, posture_color = analyze_posture(frame, landmarks)
            
#             # Analyze focus (blink detection)
#             blink_count = analyze_focus(frame)

#             # Draw the pose landmarks and angles
#             mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#             cv2.putText(frame, posture_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, posture_color, 2, cv2.LINE_AA)
#             cv2.putText(frame, f"Blinks: {blink_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

#         # Encode the frame to JPEG
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_encoded = base64.b64encode(buffer).decode('utf-8')

#         # Yield the encoded frame, posture status, and blink count
#         yield frame_encoded, posture_status, blink_count
    
#     cap.release()

import cv2
import mediapipe as mp
import base64
import numpy as np
import time
from playsound import playsound
import os
from collections import deque

# Mediapipe initialization
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# Initialize variables for blink detection
previous_blink_state = False
blink_count = 0
blink_history = []
blink_smooth_window = deque(maxlen=5)  # Moving average for blink detection

# Variables for angle-based posture detection and calibration
is_calibrated = False
calibration_frames = 0
calibration_shoulder_angles = []
calibration_neck_angles = []
shoulder_threshold = None
neck_threshold = None
posture_smooth_window = deque(maxlen=5)  # Moving average for posture detection
last_alert_time = time.time()
alert_cooldown = 10  # seconds
sound_file = "alert_sound.mp3"  # Path to your sound file

# Increase the number of frames for calibration to increase stability
calibration_frames_target = 50  # Increase calibration frames from 30 to 50

# Function to calculate the angle between three points
def calculate_angle(point1, point2, point3):
    a = np.array(point1)
    b = np.array(point2)
    c = np.array(point3)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.degrees(np.arccos(cosine_angle))
    
    return angle

# Function to draw angles on the frame
def draw_angle(frame, point1, point2, point3, angle, color):
    cv2.putText(frame, str(int(angle)), 
                tuple(np.add(point2, (10, -10)).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

# Function to analyze posture based on angles with smoothing
def analyze_posture(frame, landmarks):
    global is_calibrated, calibration_frames, shoulder_threshold, neck_threshold, last_alert_time
    
    # Extract key landmarks
    left_shoulder = (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]),
                     int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0]))
    right_shoulder = (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame.shape[1]),
                      int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame.shape[0]))
    left_ear = (int(landmarks[mp_pose.PoseLandmark.LEFT_EAR].x * frame.shape[1]),
                int(landmarks[mp_pose.PoseLandmark.LEFT_EAR].y * frame.shape[0]))

    # Calculate shoulder and neck angles
    shoulder_angle = calculate_angle(left_shoulder, right_shoulder, (right_shoulder[0], 0))
    neck_angle = calculate_angle(left_ear, left_shoulder, (left_shoulder[0], 0))

    # Calibration process
    if not is_calibrated and calibration_frames < calibration_frames_target:
        calibration_shoulder_angles.append(shoulder_angle)
        calibration_neck_angles.append(neck_angle)
        calibration_frames += 1
        return f"Calibrating... {calibration_frames}/{calibration_frames_target}", (255, 255, 0)
    
    if not is_calibrated:
        shoulder_threshold = np.mean(calibration_shoulder_angles) - 10
        neck_threshold = np.mean(calibration_neck_angles) - 10
        is_calibrated = True
        print(f"Calibration complete. Shoulder threshold: {shoulder_threshold:.1f}, Neck threshold: {neck_threshold:.1f}")

    # Add angles to smoothing window
    posture_smooth_window.append((shoulder_angle, neck_angle))

    # Apply moving average
    smooth_shoulder_angle = np.mean([angle[0] for angle in posture_smooth_window])
    smooth_neck_angle = np.mean([angle[1] for angle in posture_smooth_window])

    # Posture status check
    current_time = time.time()
    if smooth_shoulder_angle < shoulder_threshold or smooth_neck_angle < neck_threshold:
        if current_time - last_alert_time > alert_cooldown:
            print("Poor posture detected! Please sit up straight.")
            if os.path.exists(sound_file):
                playsound(sound_file)
            last_alert_time = current_time
        return "Poor Posture", (0, 0, 255)  # Red for bad posture
    else:
        return "Good Posture", (0, 255, 0)  # Green for good posture

# Function to analyze focus (blink detection) with smoothing
# Function to analyze focus (blink detection) with improved accuracy
def analyze_focus(frame):
    global previous_blink_state, blink_count, blink_history
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            left_eye_top = face_landmarks.landmark[159]
            left_eye_bottom = face_landmarks.landmark[145]
            right_eye_top = face_landmarks.landmark[386]
            right_eye_bottom = face_landmarks.landmark[374]

            left_eye_distance = abs(left_eye_top.y - left_eye_bottom.y)
            right_eye_distance = abs(right_eye_top.y - right_eye_bottom.y)
            eye_open_threshold = 0.02  # Adjust threshold for blinking detection

            # Average both eyes for more precise blink detection
            avg_eye_distance = (left_eye_distance + right_eye_distance) / 2

            # Apply moving average to smooth the blink detection
            blink_smooth_window.append(avg_eye_distance)
            smooth_eye_distance = np.mean(blink_smooth_window)

            # Check for blink
            if smooth_eye_distance < eye_open_threshold:
                if not previous_blink_state:  # Blink detected
                    blink_count += 1  # Increment the blink count
                    previous_blink_state = True
                    blink_history.append(time.time())  # Log blink time
            else:
                previous_blink_state = False  # Reset blink state when eyes are open

    # Keep only blinks from the last minute
    current_time = time.time()
    blink_history = [t for t in blink_history if current_time - t < 60]  # Only keep blinks from the last minute

    return blink_count  # Return the total blink count, which should never decrease


# Function to generate video frames with posture and blink analysis
def generate_frame():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera could not be opened.")
        return

    global blink_count  # Use global blink_count to keep track
    blink_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Convert frame to RGB for pose detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Analyze posture
            posture_status, posture_color = analyze_posture(frame, landmarks)
            
            # Analyze focus (blink detection)
            blink_count = analyze_focus(frame)

            # Draw the pose landmarks and angles
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            cv2.putText(frame, posture_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, posture_color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"Blinks: {blink_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Encode the frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_encoded = base64.b64encode(buffer).decode('utf-8')

        # Yield the encoded frame, posture status, and blink count
        yield frame_encoded, posture_status, blink_count
    
    cap.release()


