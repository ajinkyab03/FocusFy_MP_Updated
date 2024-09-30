export const startWebcam = async () => {
    const response = await fetch('/start-webcam', { method: 'POST' });
    return response.json();
  };
  
  export const stopWebcam = async () => {
    const response = await fetch('/stop-webcam', { method: 'POST' });
    return response.json();
  };
  