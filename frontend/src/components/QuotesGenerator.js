import React, { useState, useEffect } from 'react';
import twitterIcon from './assets/twitter.png';
import tumblrIcon from './assets/loader.png';

const Quotes = () => {
  const [quote, setQuote] = useState('');
  const [author, setAuthor] = useState('');
  const [minutes, setMinutes] = useState(''); // State to store user input time in minutes
  const [isVisible, setIsVisible] = useState(true); // State to control visibility
  const [remainingTime, setRemainingTime] = useState(0); // State for remaining time in seconds

  useEffect(() => {
    getQuote();
  }, []);

  const getQuote = () => {
    const url = `https://gist.githubusercontent.com/camperbot/5a022b72e96c4c9585c32bf6a75f62d9/raw/e3c6895ce42069f0ee7e991229064f167fe8ccdc/quotes.json`;
    fetch(url)
      .then(res => res.json())
      .then(data => {
        const dataQuotes = data.quotes;
        const randomNum = Math.floor(Math.random() * dataQuotes.length);
        const randomQuote = dataQuotes[randomNum];

        setQuote(randomQuote.quote);
        setAuthor(randomQuote.author);
      });
  };

  const handleClick = () => {
    getQuote();
  };

  const handleStartTimer = () => {
    const timeInMinutes = parseInt(minutes, 10);
    if (!isNaN(timeInMinutes) && timeInMinutes > 0) {
      setIsVisible(true);
      const totalTimeInSeconds = timeInMinutes * 60;
      setRemainingTime(totalTimeInSeconds);
      
      const interval = setInterval(() => {
        setRemainingTime(prev => {
          if (prev <= 1) {
            clearInterval(interval); // Clear the interval when time is up
            setIsVisible(false); // Make component invisible when time is up
            return 0; // Prevent negative seconds
          }
          return prev - 1; // Decrease the remaining time
        });
      }, 1000); // Update every second
    } else {
      alert("Please enter a valid number of minutes.");
    }
  };

  // Format remaining time in MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`; // Ensures seconds are always two digits
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-r from-purple-600 to-blue-500 p-6 sm:p-10 lg:p-20">
      {isVisible && (
        <div id="quote-box" className="bg-white dark:bg-gray-900 p-6 sm:p-8 lg:p-10 rounded-3xl shadow-xl max-w-xs sm:max-w-md lg:max-w-lg text-center">
          <div id="text" className="mb-4">
            <p className="text-xl sm:text-2xl lg:text-3xl font-semibold text-gray-900 dark:text-gray-300">"{quote}"</p>
          </div>
          <div id="author" className="mb-8">
            <p className="text-lg sm:text-xl font-light text-gray-700 dark:text-gray-400">- {author}</p>
          </div>

          <div id="buttons" className="flex justify-around items-center mb-8">
            <a href="#" id="twet-quote">
              <img src={twitterIcon} alt="Twitter" className="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 hover:scale-105 transition-transform duration-300" />
            </a>
            <a href="#" id="tumlr-quote">
              <img src={tumblrIcon} alt="Tumblr" className="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 hover:scale-105 transition-transform duration-300" />
            </a>
          </div>
          <button 
            onClick={handleClick} 
            id="new-quote"
            className="w-full py-2 sm:py-3 lg:py-4 px-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-bold rounded-lg shadow-lg hover:scale-105 transition-transform duration-300"
          >
            New Quote
          </button>
          <div id="timer" className="mt-4">
            <p className="text-md sm:text-lg lg:text-xl font-semibold text-gray-900 dark:text-gray-300">Time Remaining: {formatTime(remainingTime)}</p>
          </div>
        </div>
      )}

      <div className="mt-8 flex flex-col items-center">
        <input
          type="number"
          value={minutes}
          onChange={(e) => setMinutes(e.target.value)}
          placeholder="Enter time in minutes"
          className="w-40 sm:w-64 lg:w-80 p-2 sm:p-3 text-lg rounded-lg shadow-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
        />
        <button 
          onClick={handleStartTimer} 
          className="w-40 sm:w-64 lg:w-80 py-2 sm:py-3 lg:py-4 px-4 bg-gradient-to-r from-green-400 to-green-600 text-white font-bold rounded-lg shadow-lg hover:scale-105 transition-transform duration-300"
        >
          Start Timer
        </button>
      </div>
    </div>
  );
};

export default Quotes;
