import React, { useState } from 'react';
import { startWebcam, stopWebcam } from './api';

function WebcamPage() {
  const [webcamActive, setWebcamActive] = useState(false);

  const handleStart = async () => {
    const response = await startWebcam();
    setWebcamActive(true);
  };

  const handleStop = async () => {
    const response = await stopWebcam();
    setWebcamActive(false);
  };

  return (
    <div>
      <button onClick={handleStart}>Start Webcam</button>
      <button onClick={handleStop}>Stop Webcam</button>
      {webcamActive && <div>Webcam feed and posture detection here</div>}
    </div>
  );
}

export default WebcamPage;
