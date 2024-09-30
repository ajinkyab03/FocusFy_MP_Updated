from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pymongo
import posture_detector  # Ensure this module is implemented correctly
import time
import threading

app = Flask(__name__)
CORS(app)

# MongoDB Client Setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['webcam_db']
timing_collection = db['timing']

# Global Variables
current_session_id = None
current_blink_count = 0
posture_data = []  # To store posture data over time
focus_score = 100  # Start with a full score

@app.route('/start-webcam', methods=['POST'])
def start_webcam():
    global current_session_id, current_blink_count, posture_data, focus_score
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
    global current_session_id
    try:
        stop_time = datetime.now()
        # Update the document with the stop time, blink count, posture data, and focus score
        timing_collection.update_one(
            {"_id": current_session_id},
            {"$set": {"stop_time": stop_time, "blink_count": current_blink_count, "posture_data": posture_data, "focus": focus_score}}
        )
        return jsonify({"message": "Webcam stopped", "stop_time": str(stop_time)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/video-feed')
def video_feed():
    def generate():
        global current_blink_count, posture_data, focus_score
        for frame, posture, blink_count in posture_detector.generate_frame():
            current_blink_count = blink_count
            
            # Add posture to the data array every defined interval
            if len(posture_data) % 10 == 0:  # Adjust based on the frame rate
                posture_data.append(posture)
            
            # Calculate focus based on blinks and posture
            focus_score = calculate_focus(current_blink_count, posture_data)

            yield f"data: {frame},{posture},{current_blink_count},{focus_score}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

def calculate_focus(blink_count, posture_data):
    max_blinks = 5  # Max blinks in a minute for good focus
    blink_score = max(0, (max_blinks - blink_count)) / max_blinks * 100
    posture_score = sum(1 for p in posture_data if p == "good posture") / len(posture_data) * 100 if posture_data else 0
    
    # Weighted average
    focus_percentage = (0.7 * blink_score) + (0.3 * posture_score)
    return round(focus_percentage, 2)

def log_interval_data(start_time):
    global current_blink_count, posture_data, focus_score
    while True:
        time.sleep(6)  # Wait for 10 minutes
        current_time = datetime.now()

        elapsed_time=(current_time-start_time).total_seconds()
        
        # Log the current state every 10 minutes
        interval_data = {
            "timestamp": current_time,
            "blink_count": current_blink_count,
            "posture_data": posture_data[-10:],  # Get the last 10 entries of posture data
            "focus": focus_score,
            "elapsed_time":elapsed_time
        }

        # Update the session data in MongoDB
        timing_collection.update_one(
            {"_id": current_session_id},
            {"$push": {"interval_data": interval_data}}  # Store interval data
        )

if __name__ == '__main__':
    app.run(debug=True)
