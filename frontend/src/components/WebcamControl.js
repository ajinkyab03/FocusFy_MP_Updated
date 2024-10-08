import React, { useEffect, useRef, useState } from 'react';
import Timetable from './Timetable';
import QuotesGenerator from './QuotesGenerator';

const WebcamControl = () => {
    const videoRef = useRef(null);
    const [posture, setPosture] = useState("");
    const [blinkCount, setBlinkCount] = useState(0);
    const [focusPercentage, setFocusPercentage] = useState(100); // Start with 100% focus
    const [eventSource, setEventSource] = useState(null);

    const startWebcam = async () => {
        try {
            const response = await fetch('http://localhost:5000/start-webcam', { method: 'POST' });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const es = new EventSource('http://localhost:5000/video-feed');
            setEventSource(es);

            es.onmessage = function(event) {
                const [frameData, postureData, blinkData, focusData] = event.data.split(",");

                if (videoRef.current) {
                    const imageBlob = `data:image/jpeg;base64,${frameData}`;
                    videoRef.current.src = imageBlob;
                }

                setPosture(postureData);
                setBlinkCount(Number(blinkData));
                setFocusPercentage(Number(focusData)); // Update focus percentage
            };
        } catch (error) {
            console.error('Error starting webcam:', error);
        }
    };

    const stopWebcam = async () => {
        try {
            const response = await fetch('http://localhost:5000/stop-webcam', { method: 'POST' });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            if (eventSource) {
                eventSource.close();
                setEventSource(null);
            }
        } catch (error) {
            console.error('Error stopping webcam:', error);
        }
    };

    return (
        <div className="relative h-screen bg-gradient-to-r from-blue-500 to-purple-500 p-10">
            <div className="max-w-lg mx-auto bg-white dark:bg-gray-900 p-8 rounded-3xl shadow-xl">
                <h1 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-gray-300">Webcam Feed</h1>
                
                <div className="flex justify-center items-center mb-4">
                    <img 
                        ref={videoRef} 
                        alt="Webcam Feed" 
                        className="rounded-xl shadow-md w-72 h-48 object-cover transition-transform transform hover:scale-105 duration-300" 
                    />
                </div>

                <div className="text-center text-lg mb-4">
                    <p className="dark:text-gray-300 text-gray-700">Posture Status: <span className="font-semibold">{posture}</span></p>
                    <p className="dark:text-gray-300 text-gray-700">Blink Count: <span className="font-semibold">{blinkCount}</span></p>
                    <p className="dark:text-gray-300 text-gray-700">Focus Percentage: <span className="font-semibold">{focusPercentage.toFixed(2)}%</span></p>
                </div>

                <div className="flex justify-between mt-8">
                    <button 
                        className="w-full mx-2 p-3 text-white bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg hover:scale-105 transition transform duration-300 shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onClick={startWebcam}
                    >
                        Start Webcam
                    </button>
                    <button 
                        className="w-full mx-2 p-3 text-white bg-gradient-to-r from-red-500 to-pink-500 rounded-lg hover:scale-105 transition transform duration-300 shadow-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                        onClick={stopWebcam}
                    >
                        Stop Webcam
                    </button>
                </div>
            </div>
        </div>
    );
};

export default WebcamControl;
