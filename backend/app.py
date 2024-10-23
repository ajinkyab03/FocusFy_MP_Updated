# from flask import Flask, Response, jsonify, request
# from flask_cors import CORS
# from datetime import datetime
# import pymongo
# import posture_detector  # Ensure this module is implemented correctly
# import time
# import threading

# app = Flask(__name__)
# CORS(app)

# # MongoDB Client Setup
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client['webcam_db']
# timing_collection = db['timing']

# # Global Variables
# current_session_id = None
# current_blink_count = 0
# posture_data = []  # To store posture data over time
# focus_percentage = 100  # Start with a full score
# video_thread = None  # Keep track of the video processing thread

# def log_interval_data(start_time):
#     global current_blink_count, posture_data, focus_percentage
#     while current_session_id:
#         time.sleep(10)  # Log data every 10 seconds
#         current_time = datetime.now()

#         # Calculate elapsed time
#         elapsed_time = (current_time - start_time).total_seconds()

#         # Log the current state every 10 seconds
#         interval_data = {
#             "timestamp": current_time,
#             "blink_count": current_blink_count,
#             "posture_data": posture_data[-10:],  # Get the last 10 entries of posture data
#             "focus_percentage": focus_percentage,  # Store current focus percentage
#             "elapsed_time": elapsed_time
#         }

#         # Update the session data in MongoDB
#         timing_collection.update_one(
#             {"_id": current_session_id},
#             {"$push": {"interval_data": interval_data}}  # Store interval data
#         )

# @app.route('/start-webcam', methods=['POST'])
# def start_webcam():
#     global current_session_id, current_blink_count, posture_data, focus_percentage, video_thread
#     try:
#         start_time = datetime.now()
#         current_blink_count = 0
#         posture_data = []  # Reset posture data when starting a new session
#         focus_percentage = 100  # Reset focus percentage

#         # Insert session start time into MongoDB
#         result = timing_collection.insert_one({
#             "start_time": start_time,
#             "blink_count": 0,
#             "posture_status": [],  # To hold an array of posture objects
#             "focus_percentage": 100,  # Initial focus percentage
#             "interval_data": []  # Initialize interval data storage
#         })
#         current_session_id = result.inserted_id

#         # Start the video feed processing in a separate thread
#         def process_video_feed():
#             global current_blink_count, posture_data, focus_percentage
#             for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
#                 if not current_session_id:
#                     break  # Stop processing if the session is no longer active

#                 current_blink_count = blink_count
#                 posture_object = {
#                     "time": time.time(),
#                     "posture": posture_status,  # Store posture as a string
#                     "blink_count": blink_count
#                 }
#                 posture_data.append(posture_object)

#                 # Adjust focus percentage based on posture and blink count
#                 if posture_status == "Poor Posture":
#                     focus_percentage = max(focus_percentage - 1, 0)  # Deduct focus percentage for poor posture
#                 else:
#                     focus_percentage = min(100, focus_percentage + 0.5)  # Slightly recover focus for good posture

#                 # Update MongoDB with the new blink count and focus percentage
#                 timing_collection.update_one(
#                     {"_id": current_session_id},
#                     {
#                         "$set": {
#                             "blink_count": current_blink_count,
#                             "posture_status": posture_data,
#                             "focus_percentage": focus_percentage
#                         }
#                     }
#                 )

#         # Start processing the webcam feed asynchronously
#         video_thread = threading.Thread(target=process_video_feed)
#         video_thread.start()

#         # Start logging interval data in a separate thread
#         interval_thread = threading.Thread(target=log_interval_data, args=(start_time,))
#         interval_thread.start()

#         return jsonify({"message": "Webcam feed started", "session_id": str(current_session_id)}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/stop-webcam', methods=['POST'])
# def stop_webcam():
#     global current_session_id, video_thread
#     try:
#         if current_session_id:
#             # Mark the session as ended
#             session_id_to_stop = current_session_id
#             current_session_id = None  # Mark session as ended
            
#             # Wait for the video thread to finish
#             if video_thread:
#                 video_thread.join()  # Ensure video processing thread stops

#             # Calculate overall focus percentage from interval data if available
#             session_data = timing_collection.find_one({"_id": session_id_to_stop})

#             if session_data and session_data.get("interval_data"):
#                 total_focus = sum(interval["focus_percentage"] for interval in session_data["interval_data"])
#                 total_intervals = len(session_data["interval_data"])

#                 overall_focus_percentage = total_focus / total_intervals if total_intervals > 0 else 0

#                 # Update the session with end time and overall focus percentage
#                 timing_collection.update_one(
#                     {"_id": session_id_to_stop},
#                     {
#                         "$set": {
#                             "end_time": datetime.now(),
#                             "focus_percentage": overall_focus_percentage  # Store overall focus percentage
#                         }
#                     }
#                 )

#             return jsonify({"message": "Webcam feed stopped", "overall_focus_percentage": overall_focus_percentage}), 200
#         else:
#             return jsonify({"message": "No active session to stop"}), 400

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/video-feed')
# def video_feed():
#     def generate():
#         global current_blink_count, posture_data, focus_percentage
#         for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
#             current_blink_count = blink_count
#             posture_data.append({"time": time.time(), "posture": posture_status})

#             # Calculate focus based on blinks and posture
#             focus_percentage = calculate_focus(current_blink_count, posture_data)

#             # Send the video feed, posture, blink count, and focus score as an event stream
#             yield f"data: {frame_encoded},{posture_status},{current_blink_count},{focus_percentage}\n\n"

#     return Response(generate(), mimetype='text/event-stream')

# def calculate_focus(blink_count, posture_data):
#     """
#     Calculate the focus percentage based on blink count and posture data.

#     Parameters:
#     - blink_count: The total number of blinks detected.
#     - posture_data: A list of dictionaries containing posture information.

#     Returns:
#     - A float representing the focus percentage, capped at 100.
#     """
    
#     # Constants
#     MAX_BLINKS_PER_MINUTE = 5  # Maximum number of blinks allowed for good focus
#     WEIGHT_BLINK_SCORE = 0.3    # Weighting factor for blink score
#     WEIGHT_POSTURE_SCORE = 0.7   # Weighting factor for posture score

#     # Calculate blink score
#     if blink_count >= MAX_BLINKS_PER_MINUTE:
#         blink_score = 0
#     else:
#         blink_score = ((MAX_BLINKS_PER_MINUTE - blink_count) / MAX_BLINKS_PER_MINUTE) * 100

#     # Calculate posture score
#     posture_score = 0
#     if posture_data:
#         good_posture_count = sum(1 for p in posture_data if p.get("posture") == "Good Posture")
#         posture_score = (good_posture_count / len(posture_data)) * 100

#     # Calculate overall focus percentage using weighted average
#     focus_percentage = (WEIGHT_BLINK_SCORE * blink_score) + (WEIGHT_POSTURE_SCORE * posture_score)

#     # Ensure focus percentage does not exceed 100
#     return round(min(focus_percentage, 100), 2)




# if __name__ == '__main__':
#     app.run(debug=True)


#this is good code
# from flask import Flask, Response, jsonify, request
# from flask_cors import CORS
# from datetime import datetime
# import pymongo
# import posture_detector  # Ensure this module is implemented correctly
# import time
# import threading

# app = Flask(__name__)
# CORS(app)

# # MongoDB Client Setup
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client['webcam_db']
# timing_collection = db['timing']

# # Global Variables
# current_session_id = None
# current_blink_count = 0
# posture_data = []  # To store posture data over time
# focus_percentage = 100  # Start with a full score
# video_thread = None  # Keep track of the video processing thread

# def log_interval_data(start_time):
#     global current_blink_count, posture_data, focus_percentage
#     while current_session_id:
#         time.sleep(10)  # Log data every 10 seconds
#         current_time = datetime.now()

#         # Calculate elapsed time
#         elapsed_time = (current_time - start_time).total_seconds()

#         # Log the current state every 10 seconds
#         interval_data = {
#             "timestamp": current_time,
#             "blink_count": current_blink_count,
#             "posture_data": posture_data[-10:],  # Get the last 10 entries of posture data
#             "focus_percentage": focus_percentage,  # Store current focus percentage
#             "elapsed_time": elapsed_time
#         }

#         # Update the session data in MongoDB
#         timing_collection.update_one(
#             {"_id": current_session_id},
#             {"$push": {"interval_data": interval_data}}  # Store interval data
#         )

# @app.route('/start-webcam', methods=['POST'])
# def start_webcam():
#     global current_session_id, current_blink_count, posture_data, focus_percentage, video_thread
#     try:
#         start_time = datetime.now()
#         current_blink_count = 0
#         posture_data = []  # Reset posture data when starting a new session
#         focus_percentage = 100  # Reset focus percentage

#         # Insert session start time into MongoDB
#         result = timing_collection.insert_one({
#             "start_time": start_time,
#             "blink_count": 0,
#             "posture_status": [],  # To hold an array of posture objects
#             "focus_percentage": 100,  # Initial focus percentage
#             "interval_data": []  # Initialize interval data storage
#         })
#         current_session_id = result.inserted_id

#         # Start the video feed processing in a separate thread
#         def process_video_feed():
#             global current_blink_count, posture_data, focus_percentage
#             for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
#                 if not current_session_id:
#                     break  # Stop processing if the session is no longer active

#                 current_blink_count = blink_count
#                 posture_object = {
#                     "time": time.time(),
#                     "posture": posture_status,  # Store posture as a string
#                     "blink_count": blink_count
#                 }
#                 posture_data.append(posture_object)

#                 # Adjust focus percentage based on posture and blink count
#                 if posture_status == "Poor Posture":
#                     focus_percentage = max(focus_percentage - 1, 0)  # Deduct focus percentage for poor posture
#                 else:
#                     focus_percentage = min(100, focus_percentage + 0.5)  # Slightly recover focus for good posture

#                 # Update MongoDB with the new blink count and focus percentage
#                 timing_collection.update_one(
#                     {"_id": current_session_id},
#                     {
#                         "$set": {
#                             "blink_count": current_blink_count,
#                             "posture_status": posture_data,
#                             "focus_percentage": focus_percentage
#                         }
#                     }
#                 )

#         # Start processing the webcam feed asynchronously
#         video_thread = threading.Thread(target=process_video_feed)
#         video_thread.start()

#         # Start logging interval data in a separate thread
#         interval_thread = threading.Thread(target=log_interval_data, args=(start_time,))
#         interval_thread.start()

#         return jsonify({"message": "Webcam feed started", "session_id": str(current_session_id)}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/stop-webcam', methods=['POST'])
# def stop_webcam():
#     global current_session_id, video_thread
#     try:
#         if current_session_id:
#             # Mark the session as ended
#             session_id_to_stop = current_session_id
#             current_session_id = None  # Mark session as ended
            
#             # Wait for the video thread to finish
#             if video_thread:
#                 video_thread.join()  # Ensure video processing thread stops

#             # Calculate overall focus percentage from interval data if available
#             session_data = timing_collection.find_one({"_id": session_id_to_stop})

#             if session_data and session_data.get("interval_data"):
#                 total_focus = sum(interval["focus_percentage"] for interval in session_data["interval_data"])
#                 total_intervals = len(session_data["interval_data"])

#                 overall_focus_percentage = total_focus / total_intervals if total_intervals > 0 else 0

#                 # Update the session with end time and overall focus percentage
#                 timing_collection.update_one(
#                     {"_id": session_id_to_stop},
#                     {
#                         "$set": {
#                             "end_time": datetime.now(),
#                             "focus_percentage": overall_focus_percentage  # Store overall focus percentage
#                         }
#                     }
#                 )

#             return jsonify({"message": "Webcam feed stopped", "overall_focus_percentage": overall_focus_percentage}), 200
#         else:
#             return jsonify({"message": "No active session to stop"}), 400

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/video-feed')
# def video_feed():
#     def generate():
#         global current_blink_count, posture_data, focus_percentage
#         for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
#             current_blink_count = blink_count
#             posture_data.append({"time": time.time(), "posture": posture_status})

#             # Calculate focus based on blinks, posture, and interval data
#             session_data = timing_collection.find_one({"_id": current_session_id})
#             interval_data = session_data.get("interval_data", []) if session_data else []
#             focus_percentage = calculate_focus(current_blink_count, posture_data, interval_data)

#             # Send the video feed, posture, blink count, and focus score as an event stream
#             yield f"data: {frame_encoded},{posture_status},{current_blink_count},{focus_percentage}\n\n"

#     return Response(generate(), mimetype='text/event-stream')

# def calculate_focus(blink_count, posture_data, interval_data):
#     """
#     Calculate the focus percentage based on blink count, posture data, and interval data.

#     Parameters:
#     - blink_count: The total number of blinks detected.
#     - posture_data: A list of dictionaries containing posture information.
#     - interval_data: A list of dictionaries containing blink counts and elapsed time for each interval.

#     Returns:
#     - A float representing the focus percentage, capped at 100.
#     """

#     # Constants
#     BLINKS_REQUIRED_PER_SECOND = 0.5  # 0.5 blinks required per second for good focus
#     WEIGHT_BLINK_SCORE = 0.3          # Weighting factor for blink score
#     WEIGHT_POSTURE_SCORE = 0.7         # Weighting factor for posture score

#     # Calculate total expected blinks based on interval data
#     total_expected_blinks = 0
#     for interval in interval_data:
#         elapsed_time = interval.get("elapsed_time", 0)  # Ensure there's an elapsed time
#         total_expected_blinks += elapsed_time * BLINKS_REQUIRED_PER_SECOND

#     # Calculate blink score
#     if total_expected_blinks > 0:
#         blink_score = max(0, (total_expected_blinks - blink_count) / total_expected_blinks * 100)
#     else:
#         blink_score = 0

#     # Calculate posture score
#     posture_score = 0
#     if posture_data:
#         good_posture_count = sum(1 for p in posture_data if p.get("posture") == "Good Posture")
#         posture_score = (good_posture_count / len(posture_data)) * 100

#     # Calculate overall focus percentage using weighted average
#     focus_percentage = (WEIGHT_BLINK_SCORE * blink_score) + (WEIGHT_POSTURE_SCORE * posture_score)

#     # Ensure focus percentage does not exceed 100
#     return round(min(focus_percentage, 100), 2)

# if __name__ == '__main__':
#     app.run(debug=True)



#this is better code

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
focus_percentage = 100  # Start with a full score
video_thread = None  # Keep track of the video processing thread

def log_interval_data(start_time):
    global current_blink_count, posture_data, focus_percentage
    while current_session_id:
        time.sleep(10)  # Log data every 10 seconds
        current_time = datetime.now()

        # Calculate elapsed time
        elapsed_time = (current_time - start_time).total_seconds()

        # Log the current state every 10 seconds
        interval_data = {
            "timestamp": current_time,
            "blink_count": current_blink_count,
            "posture_data": posture_data[-10:],  # Get the last 10 entries of posture data
            "focus_percentage": focus_percentage,  # Store current focus percentage
            "elapsed_time": elapsed_time
        }

        # Update the session data in MongoDB
        timing_collection.update_one(
            {"_id": current_session_id},
            {"$push": {"interval_data": interval_data}}  # Store interval data
        )

@app.route('/start-webcam', methods=['POST'])
def start_webcam():
    global current_session_id, current_blink_count, posture_data, focus_percentage, video_thread
    try:
        start_time = datetime.now()
        current_blink_count = 0
        posture_data = []  # Reset posture data when starting a new session
        focus_percentage = 100  # Reset focus percentage

        # Insert session start time into MongoDB
        result = timing_collection.insert_one({
            "start_time": start_time,
            "blink_count": 0,
            "posture_status": [],  # To hold an array of posture objects
            "focus_percentage": 100,  # Initial focus percentage
            "interval_data": []  # Initialize interval data storage
        })
        current_session_id = result.inserted_id

        # Start the video feed processing in a separate thread
        def process_video_feed():
            global current_blink_count, posture_data, focus_percentage
            for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
                if not current_session_id:
                    break  # Stop processing if the session is no longer active

                # Update the blink count from the frame processing
                current_blink_count = blink_count
                posture_object = {
                    "time": time.time(),
                    "posture": posture_status,  # Store posture as a string
                    "blink_count": blink_count
                }
                posture_data.append(posture_object)

                # Adjust focus percentage based on posture and blink count
                if posture_status == "Poor Posture":
                    focus_percentage = max(focus_percentage - 1, 0)  # Deduct focus percentage for poor posture
                else:
                    focus_percentage = min(100, focus_percentage + 0.5)  # Slightly recover focus for good posture
                
                if focus_percentage < 50:
                    playsound('alert.mp3')
                # Update MongoDB with the new blink count and focus percentage
                timing_collection.update_one(
                    {"_id": current_session_id},
                    {
                        "$set": {
                            "blink_count": current_blink_count,  # Update blink count
                            "posture_status": posture_data,  # Update posture data
                            "focus_percentage": focus_percentage  # Update focus percentage
                        }
                    }
                )

        # Start processing the webcam feed asynchronously
        video_thread = threading.Thread(target=process_video_feed)
        video_thread.start()

        # Start logging interval data in a separate thread
        interval_thread = threading.Thread(target=log_interval_data, args=(start_time,))
        interval_thread.start()

        return jsonify({"message": "Webcam feed started", "session_id": str(current_session_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stop-webcam', methods=['POST'])
def stop_webcam():
    global current_session_id, video_thread
    try:
        if current_session_id:
            # Mark the session as ended
            session_id_to_stop = current_session_id
            current_session_id = None  # Mark session as ended
            
            # Wait for the video thread to finish
            if video_thread:
                video_thread.join()  # Ensure video processing thread stops

            # Calculate overall focus percentage from interval data if available
            session_data = timing_collection.find_one({"_id": session_id_to_stop})

            if session_data and session_data.get("interval_data"):
                total_focus = sum(interval["focus_percentage"] for interval in session_data["interval_data"])
                total_intervals = len(session_data["interval_data"])

                overall_focus_percentage = total_focus / total_intervals if total_intervals > 0 else 0

                # Update the session with end time and overall focus percentage
                timing_collection.update_one(
                    {"_id": session_id_to_stop},
                    {
                        "$set": {
                            "end_time": datetime.now(),
                            "focus_percentage": overall_focus_percentage,  # Store overall focus percentage
                            "blink_count": current_blink_count  # Ensure the final blink count is stored
                        }
                    }
                )

            return jsonify({"message": "Webcam feed stopped", "overall_focus_percentage": overall_focus_percentage}), 200
        else:
            return jsonify({"message": "No active session to stop"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/video-feed')
def video_feed():
    def generate():
        global current_blink_count, posture_data, focus_percentage
        for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
            current_blink_count = blink_count
            posture_data.append({"time": time.time(), "posture": posture_status})

            # Calculate focus based on blinks, posture, and interval data
            session_data = timing_collection.find_one({"_id": current_session_id})
            interval_data = session_data.get("interval_data", []) if session_data else []
            focus_percentage = calculate_focus(current_blink_count, posture_data, interval_data)

            # Send the video feed, posture, blink count, and focus score as an event stream
            yield f"data: {frame_encoded},{posture_status},{current_blink_count},{focus_percentage}\n\n"

    return Response(generate(), mimetype='text/event-stream')

def calculate_focus(blink_count, posture_data, interval_data):
    """
    Calculate the focus percentage based on blink count, posture data, and interval data.

    Parameters:
    - blink_count: The total number of blinks detected.
    - posture_data: A list of dictionaries containing posture information.
    - interval_data: A list of dictionaries containing blink counts and elapsed time for each interval.

    Returns:
    - A float representing the focus percentage, capped at 100.
    """

    # Constants
    BLINKS_REQUIRED_PER_SECOND = 0.28  # 0.28 blinks required per second for good focus as 17 for minute
    WEIGHT_BLINK_SCORE = 0.3          # Weighting factor for blink score
    WEIGHT_POSTURE_SCORE = 0.7         # Weighting factor for posture score

    # Calculate total expected blinks based on interval data
    total_expected_blinks = 0
    for interval in interval_data:
        elapsed_time = interval.get("elapsed_time", 0)  # Ensure there's an elapsed time
        total_expected_blinks += elapsed_time * BLINKS_REQUIRED_PER_SECOND

    # Calculate blink score
    if total_expected_blinks > 0:
        blink_score = max(0, (total_expected_blinks - blink_count) / total_expected_blinks * 100)
    else:
        blink_score = 0

    # Calculate posture score
    posture_score = 0
    if posture_data:
        good_posture_count = sum(1 for p in posture_data if p.get("posture") == "Good Posture")
        posture_score = (good_posture_count / len(posture_data)) * 100

    # Calculate overall focus percentage using weighted average
    focus_percentage = (WEIGHT_BLINK_SCORE * blink_score) + (WEIGHT_POSTURE_SCORE * posture_score)

    # Ensure focus percentage does not exceed 100
    return round(min(focus_percentage, 100), 2)

if __name__ == '__main__':
    app.run(debug=True)




# better than above but posture problem
# from flask import Flask, Response, jsonify, request
# from flask_cors import CORS
# from datetime import datetime
# import pymongo
# import posture_detector  # Ensure this module is implemented correctly
# import time
# import threading
# from playsound import playsound  # Import playsound to play audio

# app = Flask(__name__)
# CORS(app)

# # MongoDB Client Setup
# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client['webcam_db']
# timing_collection = db['timing']

# # Global Variables
# current_session_id = None
# current_blink_count = 0
# posture_data = []  # To store posture data over time
# focus_percentage = 100  # Start with a full score
# video_thread = None  # Keep track of the video processing thread

# def log_interval_data(start_time):
#     global current_blink_count, posture_data, focus_percentage
#     while current_session_id:
#         time.sleep(10)  # Log data every 10 seconds
#         current_time = datetime.now()

#         # Calculate elapsed time
#         elapsed_time = (current_time - start_time).total_seconds()

#         # Log the current state every 10 seconds
#         interval_data = {
#             "timestamp": current_time,
#             "blink_count": current_blink_count,
#             "posture_data": posture_data[-10:],  # Get the last 10 entries of posture data
#             "focus_percentage": focus_percentage,  # Store current focus percentage
#             "elapsed_time": elapsed_time
#         }

#         # Update the session data in MongoDB
#         timing_collection.update_one(
#             {"_id": current_session_id},
#             {"$push": {"interval_data": interval_data}}  # Store interval data
#         )

# @app.route('/start-webcam', methods=['POST'])
# def start_webcam():
#     global current_session_id, current_blink_count, posture_data, focus_percentage, video_thread
#     try:
#         start_time = datetime.now()
#         current_blink_count = 0
#         posture_data = []  # Reset posture data when starting a new session
#         focus_percentage = 100  # Reset focus percentage

#         # Insert session start time into MongoDB
#         result = timing_collection.insert_one({
#             "start_time": start_time,
#             "blink_count": 0,
#             "posture_status": [],  # To hold an array of posture objects
#             "focus_percentage": 100,  # Initial focus percentage
#             "interval_data": []  # Initialize interval data storage
#         })
#         current_session_id = result.inserted_id

#         # Start the video feed processing in a separate thread
#         def process_video_feed():
#             global current_blink_count, posture_data, focus_percentage
#             for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
#                 if not current_session_id:
#                     break  # Stop processing if the session is no longer active

#                 current_blink_count = blink_count
#                 posture_object = {
#                     "time": time.time(),
#                     "posture": posture_status,  # Store posture as a string
#                     "blink_count": blink_count
#                 }
#                 posture_data.append(posture_object)

#                 # Adjust focus percentage based on posture and blink count
#                 if posture_status == "Poor Posture":
#                     focus_percentage = max(focus_percentage - 1, 0)  # Deduct focus percentage for poor posture
#                 else:
#                     focus_percentage = min(100, focus_percentage + 0.5)  # Slightly recover focus for good posture

#                 # Check if focus percentage falls below 50% and play sound
#                 if focus_percentage < 50:
#                     playsound('alert.mp3')  # Play alert sound

#                 # Update MongoDB with the new blink count and focus percentage
#                 timing_collection.update_one(
#                     {"_id": current_session_id},
#                     {
#                         "$set": {
#                             "blink_count": current_blink_count,
#                             "posture_status": posture_data,
#                             "focus_percentage": focus_percentage
#                         }
#                     }
#                 )

#         # Start processing the webcam feed asynchronously
#         video_thread = threading.Thread(target=process_video_feed)
#         video_thread.start()

#         # Start logging interval data in a separate thread
#         interval_thread = threading.Thread(target=log_interval_data, args=(start_time,))
#         interval_thread.start()

#         return jsonify({"message": "Webcam feed started", "session_id": str(current_session_id)}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/stop-webcam', methods=['POST'])
# def stop_webcam():
#     global current_session_id, video_thread
#     try:
#         if current_session_id:
#             # Mark the session as ended
#             session_id_to_stop = current_session_id
#             current_session_id = None  # Mark session as ended
            
#             # Wait for the video thread to finish
#             if video_thread:
#                 video_thread.join()  # Ensure video processing thread stops

#             # Calculate overall focus percentage from interval data if available
#             session_data = timing_collection.find_one({"_id": session_id_to_stop})

#             if session_data and session_data.get("interval_data"):
#                 total_focus = sum(interval["focus_percentage"] for interval in session_data["interval_data"])
#                 total_intervals = len(session_data["interval_data"])

#                 overall_focus_percentage = total_focus / total_intervals if total_intervals > 0 else 0

#                 # Update the session with end time and overall focus percentage
#                 timing_collection.update_one(
#                     {"_id": session_id_to_stop},
#                     {
#                         "$set": {
#                             "end_time": datetime.now(),
#                             "focus_percentage": overall_focus_percentage  # Store overall focus percentage
#                         }
#                     }
#                 )

#             return jsonify({"message": "Webcam feed stopped", "overall_focus_percentage": overall_focus_percentage}), 200
#         else:
#             return jsonify({"message": "No active session to stop"}), 400

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/video-feed')
# def video_feed():
#     def generate():
#         global current_blink_count, posture_data, focus_percentage
#         for frame_encoded, posture_status, blink_count in posture_detector.generate_frame():
#             current_blink_count = blink_count
#             posture_data.append({"time": time.time(), "posture": posture_status})

#             # Calculate focus based on blinks, posture, and interval data
#             session_data = timing_collection.find_one({"_id": current_session_id})
#             interval_data = session_data.get("interval_data", []) if session_data else []
#             focus_percentage = calculate_focus(current_blink_count, posture_data, interval_data)

#             # Send the video feed, posture, blink count, and focus score as an event stream
#             yield f"data: {frame_encoded},{posture_status},{current_blink_count},{focus_percentage}\n\n"

#     return Response(generate(), mimetype='text/event-stream')

# def calculate_focus(blink_count, posture_data, interval_data):
#     """
#     Calculate the focus percentage based on blink count, posture data, and interval data.

#     Parameters:
#     - blink_count: The total number of blinks detected.
#     - posture_data: A list of dictionaries containing posture information.
#     - interval_data: A list of dictionaries containing blink counts and elapsed time for each interval.

#     Returns:
#     - A float representing the focus percentage, capped at 100.
#     """

#     # Constants
#     BLINKS_REQUIRED_PER_SECOND = 0.5  # 0.5 blinks required per second for good focus
#     WEIGHT_BLINK_SCORE = 0.3          # Weighting factor for blink score
#     WEIGHT_POSTURE_SCORE = 0.7         # Weighting factor for posture score

#     # Calculate total expected blinks based on interval data
#     total_expected_blinks = 0
#     for interval in interval_data:
#         elapsed_time = interval.get("elapsed_time", 0)  # Ensure there's an elapsed time
#         total_expected_blinks += elapsed_time * BLINKS_REQUIRED_PER_SECOND

#     # Calculate blink score
#     if total_expected_blinks > 0:
#         blink_score = max(0, (total_expected_blinks - blink_count) / total_expected_blinks * 100)
#     else:
#         blink_score = 0

#     # Calculate posture score
#     posture_score = 0
#     if posture_data:
#         good_posture_count = sum(1 for p in posture_data if p.get("posture") == "Good Posture")
#         posture_score = (good_posture_count / len(posture_data)) * 100

#     # Calculate overall focus percentage using weighted average
#     focus_percentage = (WEIGHT_BLINK_SCORE * blink_score) + (WEIGHT_POSTURE_SCORE * posture_score)

#     # Ensure focus percentage does not exceed 100
#     return round(min(focus_percentage, 100), 2)

# if __name__ == '__main__':
#     app.run(debug=True)