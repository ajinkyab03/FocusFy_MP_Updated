from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pymongo
import posture_detector  
import time
import threading

app = Flask(__name__)
CORS(app)


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['webcam_db']
timing_collection = db['timing']


current_session_id = None
current_blink_count = 0
posture_data = [] 
focus_score = 100  # Start with a full score
start_time = None  # Track session start time

@app.route('/start-webcam', methods=['POST'])
def start_webcam():
    global current_session_id, current_blink_count, posture_data, focus_score, start_time
    try:
        start_time = datetime.now()
        current_blink_count = 0
        posture_data = []  # Reset posture data when starting a new session
        focus_score = 100  # Reset focus score

        # Insert session start time into MongoDB
        result = timing_collection.insert_one({"start_time": start_time, "blink_count": current_blink_count})
        current_session_id = result.inserted_id

        # Start logging data in a separate thread
        threading.Thread(target=log_interval_data, args=(start_time,)).start()

        return jsonify({"message": "Webcam started", "start_time": str(start_time)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop-webcam', methods=['POST'])
def stop_webcam():
    global current_session_id, start_time
    try:
        stop_time = datetime.now()
        session_duration = (stop_time - start_time).total_seconds()  # Calculate session duration

        # Update the document with the stop time, blink count, posture data, focus score, and session duration
        timing_collection.update_one(
            {"_id": current_session_id},
            {"$set": {
                "stop_time": stop_time,
                "blink_count": current_blink_count,
                "posture_data": posture_data,
                "focus": focus_score,
                "session_duration": session_duration  # Store session duration in seconds
            }}
        )
        return jsonify({"message": "Webcam stopped", "stop_time": str(stop_time), "session_duration": session_duration})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/video-feed')
def video_feed():
    def generate():
        global current_blink_count, posture_data, focus_score, start_time
        for frame, posture, blink_count in posture_detector.generate_frame():
            current_blink_count = blink_count
            
            # Add posture to the data array every defined interval
            # if len(posture_data) % 10 == 0:  # Adjust based on the frame rate
            posture_data.append(posture)

            # Calculate session duration based on the current time
            session_duration = (datetime.now() - start_time).total_seconds()

            # Calculate focus based on blinks and posture
            focus_score = calculate_focus(current_blink_count, posture_data, session_duration)

            yield f"data: {frame},{posture},{current_blink_count},{focus_score}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

def calculate_focus(blink_count, posture_data, session_duration_seconds):
    base_focus_score = 50.0  # Start with a base focus score of 50%

    required_blink_rate = 0.2  # Ideal blinks per second
    expected_blink_count = session_duration_seconds * required_blink_rate

    # Print debugging to check incoming data
    print(f"Blink Count: {blink_count}, Posture Data: {posture_data}, Session Duration: {session_duration_seconds}")

    # POSTURE SCORING
    good_posture_count = sum(1 for p in posture_data if p == "good posture")
    total_posture_count = len(posture_data)
    
    if total_posture_count > 0:
        posture_focus_percentage = (good_posture_count / total_posture_count) * 100
    else:
        posture_focus_percentage = 50  # Default to neutral if no data
    
    # Print posture percentage
    print(f"Posture Focus Percentage: {posture_focus_percentage}")

    # Adjust base focus score based on posture
    if posture_focus_percentage < 50:
        posture_penalty = (50 - posture_focus_percentage) * 0.5
        base_focus_score -= posture_penalty
    else:
        posture_bonus = (posture_focus_percentage - 50) * 0.5
        base_focus_score += posture_bonus

    # BLINK SCORING
    if expected_blink_count > 0:
        blink_focus_percentage = min((blink_count / expected_blink_count) * 100, 100)
    else:
        blink_focus_percentage = 100  # Assume max focus if no expected blinks

    # Print blink percentage
    print(f"Blink Focus Percentage: {blink_focus_percentage}")

    # Adjust base focus score based on blinking
    if blink_focus_percentage < 80:
        blink_penalty = (80 - blink_focus_percentage) * 0.5
        base_focus_score -= blink_penalty
    else:
        blink_bonus = (blink_focus_percentage - 80) * 0.2
        base_focus_score += blink_bonus

    # Fatigue Penalty for long sessions
    if session_duration_seconds > 1800:
        fatigue_penalty = (session_duration_seconds - 1800) / 300  # Apply after 30 minutes
        base_focus_score -= fatigue_penalty
    
    # Print intermediate focus score
    print(f"Intermediate Focus Score (before bounding): {base_focus_score}")

    # Ensure focus score is within bounds
    overall_focus_percentage = max(0, min(base_focus_score, 100))

    # Final focus score
    print(f"Final Focus Score: {overall_focus_percentage}")

    return round(overall_focus_percentage, 2)






def log_interval_data(start_time):
    global current_blink_count, posture_data, focus_score
    while True:
        time.sleep(600)  # Wait for 10 minutes
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()  # Calculate elapsed time in seconds
        
        # Log the current state every 10 minutes
        interval_data = {
            "timestamp": current_time,
            "blink_count": current_blink_count,
            "posture_data": posture_data[-10:],  # Get the last 10 entries of posture data
            "focus": focus_score,
            "elapsed_time": elapsed_time
        }

        # Update the session data in MongoDB
        timing_collection.update_one(
            {"_id": current_session_id},
            {"$push": {"interval_data": interval_data}}  # Store interval data
        )

if __name__ == '__main__':
    app.run(debug=True)
