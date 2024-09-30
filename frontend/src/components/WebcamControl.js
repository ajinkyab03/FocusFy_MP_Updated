import React, { useEffect, useRef, useState } from 'react';

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
        <div>
            <div>
                <img ref={videoRef} alt="Webcam Feed" style={{ width: '50%%',height:"40%" }} />
                <p>Posture Status: {posture}</p>
                <p>Blink Count: {blinkCount}</p>
                <p>Focus Percentage: {focusPercentage.toFixed(2)}%</p>
            </div>

            <button onClick={startWebcam}>Start Webcam</button>
            <button onClick={stopWebcam}>Stop Webcam</button>
        </div>
    );
};

export default WebcamControl;