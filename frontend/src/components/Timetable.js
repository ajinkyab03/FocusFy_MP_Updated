import React, { useState, useEffect } from 'react';
import { jsPDF } from 'jspdf';

const Timetable = () => {
  const [subjects, setSubjects] = useState('');
  const [interval, setInterval] = useState(1); // Interval in hours
  const [breakTime, setBreakTime] = useState(15); // Break time in minutes
  const [timetable, setTimetable] = useState([]);
  const [markedItems, setMarkedItems] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [showBreaks, setShowBreaks] = useState(true); // Enable/disable breaks
  const [focusMode, setFocusMode] = useState(false); // Focus mode for distraction-free study

  // Request permission for notifications
  useEffect(() => {
    if ('Notification' in window) {
      Notification.requestPermission();
    }
  }, []);

  // Helper function for sending notifications
  const sendNotification = (title, body) => {
    if (Notification.permission === 'granted') {
      new Notification(title, { body });
    }
  };

  const generateTimetable = (subjectArray, interval) => {
    const startTime = new Date();
    let currentTime = startTime;

    const timetableWithBreaks = subjectArray.reduce((acc, subject, index) => {
      // Add the study session
      const time = new Date(currentTime.getTime());
      acc.push({
        id: index * 2, // Double the index to account for breaks
        name: subject.trim(),
        time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        marked: false,
        isBreak: false,
        startTime: new Date(currentTime), // Store the exact start time
      });

      // Trigger a notification when study starts
      setTimeout(() => sendNotification(`Time to Study: ${subject.trim()}`, `Start studying ${subject.trim()} now!`), currentTime.getTime() - startTime.getTime());

      // Move to the next study time slot
      currentTime = new Date(time.getTime() + interval * 60 * 60 * 1000);

      // Add break session after each study session (if breaks are enabled)
      if (showBreaks && index < subjectArray.length - 1) {
        const breakTimeSlot = new Date(currentTime.getTime());
        currentTime = new Date(currentTime.getTime() + breakTime * 60 * 1000); // Break time addition

        acc.push({
          id: index * 2 + 1,
          name: 'Break Time',
          time: breakTimeSlot.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          marked: false,
          isBreak: true,
        });

        // Trigger notification when break starts
        setTimeout(() => sendNotification('Break Time!', `Take a break for ${breakTime} minutes!`), breakTimeSlot.getTime() - startTime.getTime());

        // Trigger notification when break ends
        setTimeout(() => sendNotification('Break Over', 'Get back to your study session!'), currentTime.getTime() - startTime.getTime());
      }

      return acc;
    }, []);

    return timetableWithBreaks;
  };

  const handleGetTimetable = () => {
    const subjectArray = subjects.split(',').map((subj) => subj.trim());
    const newTimetable = generateTimetable(subjectArray, interval);
    setTimetable(newTimetable);
    localStorage.setItem('subjects', subjects);
    localStorage.setItem('interval', interval);
    localStorage.setItem('breakTime', breakTime);
  };

  const toggleMark = (id) => {
    const updatedTimetable = timetable.map((item) =>
      item.id === id ? { ...item, marked: !item.marked } : item
    );
    setTimetable(updatedTimetable);
    setMarkedItems(updatedTimetable.filter(item => item.marked).map(item => item.name));
    localStorage.setItem('markedItems', JSON.stringify(updatedTimetable.filter(item => item.marked).map(item => item.name)));
  };

  return (
    <div className={`min-h-screen flex items-center justify-center py-10 px-5 ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'}`}>
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-lg w-full">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">📚 Study Timetable Generator</h2>

        <textarea
          className="w-full p-4 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={subjects}
          onChange={(e) => setSubjects(e.target.value)}
          rows={4}
          placeholder="Enter subjects separated by commas"
        />

        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">
            Study Interval (hours):
          </label>
          <input
            type="number"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={interval}
            onChange={(e) => setInterval(e.target.value)}
            min="1"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">
            Break Time (minutes):
          </label>
          <input
            type="number"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={breakTime}
            onChange={(e) => setBreakTime(e.target.value)}
            min="5"
          />
        </div>

        <button
          className="w-full bg-blue-500 text-white font-semibold py-3 rounded-lg hover:bg-blue-600 transition duration-300"
          onClick={handleGetTimetable}
        >
          Get Timetable
        </button>

        {timetable.length > 0 && (
          <div className="mt-6">
            <h3 className="text-xl font-bold text-gray-700 mb-4 text-center">Your Timetable</h3>
            <ul className="space-y-2">
              {timetable.map((item) => (
                <li
                  key={item.id}
                  className={`p-3 rounded-lg cursor-pointer flex justify-between items-center ${
                    item.isBreak ? 'bg-yellow-100 border-l-4 border-yellow-500' : item.marked ? 'bg-green-100 border-l-4 border-green-500' : 'bg-gray-50'
                  }`}
                  onClick={() => toggleMark(item.id)}
                >
                  <span className={`${item.isBreak ? 'text-yellow-600' : 'text-gray-800'} font-medium`}>
                    {item.name} - {item.time}
                  </span>
                  {item.marked && (
                    <span className="text-green-600 font-bold">✔️</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        <button
          className="w-full bg-gray-700 text-white font-semibold py-3 rounded-lg mt-6 hover:bg-gray-800 transition duration-300"
          onClick={() => setFocusMode(!focusMode)}
        >
          {focusMode ? 'Exit Focus Mode' : 'Enter Focus Mode'}
        </button>

      </div>
    </div>
  );
};

export default Timetable;