import React, { useState, useEffect } from 'react';
import './App.css'; // Make sure to create this CSS file

const Timetable = () => {
  const [subjects, setSubjects] = useState('');
  const [interval, setInterval] = useState(1); // Interval in hours
  const [timetable, setTimetable] = useState([]);
  const [markedItems, setMarkedItems] = useState([]);

  useEffect(() => {
    const savedSubjects = localStorage.getItem('subjects');
    const savedMarkedItems = localStorage.getItem('markedItems');
    const savedInterval = localStorage.getItem('interval');
    if (savedSubjects) {
      setSubjects(savedSubjects);
      setTimetable(generateTimetable(savedSubjects.split(','), savedInterval ? Number(savedInterval) : 1));
    }
    if (savedMarkedItems) {
      setMarkedItems(JSON.parse(savedMarkedItems));
    }
  }, []);

  const generateTimetable = (subjectArray, interval) => {
    const startTime = new Date();
    return subjectArray.map((subject, index) => {
      const time = new Date(startTime.getTime() + index * interval * 60 * 60 * 1000);
      return {
        id: index,
        name: subject.trim(),
        time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        marked: false,
      };
    });
  };

  const handleSubjectsChange = (event) => {
    setSubjects(event.target.value);
  };

  const handleIntervalChange = (event) => {
    setInterval(event.target.value);
  };

  const handleGetTimetable = () => {
    const subjectArray = subjects.split(',').map((subj) => subj.trim());
    const newTimetable = generateTimetable(subjectArray, interval);
    setTimetable(newTimetable);
    localStorage.setItem('subjects', subjects);
    localStorage.setItem('interval', interval);
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
    <div className="timetable-container">
      <h2 className="title">📚 Study Timetable Generator</h2>
      <textarea
        className="subject-input"
        value={subjects}
        onChange={handleSubjectsChange}
        rows={4}
        placeholder="Enter subjects separated by commas"
      />
      <div className="interval-container">
        <label className="interval-label">
          Study Interval (hours):
          <input
            type="number"
            className="interval-input"
            value={interval}
            onChange={handleIntervalChange}
            min="1"
          />
        </label>
      </div>
      <button className="get-timetable-button" onClick={handleGetTimetable}>Get Timetable</button>

      {timetable.length > 0 && (
        <div className="timetable-list">
          <h3>Your Timetable:</h3>
          <ul>
            {timetable.map((item) => (
              <li key={item.id} className={`timetable-item ${item.marked ? 'marked' : ''}`} onClick={() => toggleMark(item.id)}>
                <span>
                  {item.name} - {item.time}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Timetable;
