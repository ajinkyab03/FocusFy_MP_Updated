import React from 'react';
import { Link } from 'react-router-dom';
import Logout from './Logout';

export const Navbar = ({ isLoggedIn, setIsLoggedIn }) => {
    return (
        <div className="bg-gradient-to-r from-purple-600 to-blue-500 text-white flex justify-between items-center p-4 shadow-lg">
            <h1 className="text-3xl font-extrabold tracking-tight">FocusFy</h1>
            <div className="flex items-center space-x-4">
                {!isLoggedIn ? (
                    <>
                        <Link to="/login">
                            <button className="bg-red-500 text-white font-bold py-2 px-6 rounded-full shadow-lg hover:bg-red-600 transition-all transform hover:scale-105">
                                Login
                            </button>
                        </Link>
                        <Link to="/signup">
                            <button className="bg-green-500 text-white font-bold py-2 px-6 rounded-full shadow-lg hover:bg-green-600 transition-all transform hover:scale-105">
                                Signup
                            </button>
                        </Link>
                        <Link to="/quote">
                            <button className="bg-indigo-500 text-white font-bold py-2 px-6 rounded-full shadow-lg hover:bg-indigo-600 transition-all transform hover:scale-105">
                                BreakTime
                            </button>
                        </Link>
                        <Link to="/dashboard">
                            <button className="bg-yellow-500 text-white font-bold py-2 px-6 rounded-full shadow-lg hover:bg-yellow-600 transition-all transform hover:scale-105">
                                Dashboard
                            </button>
                        </Link>
                        <Link to="/about">
                            <button className="bg-teal-500 text-white font-bold py-2 px-6 rounded-full shadow-lg hover:bg-teal-600 transition-all transform hover:scale-105">
                                About
                            </button>
                        </Link>
                    </>
                ) : (
                    <Logout setIsLoggedIn={setIsLoggedIn} />
                )}
            </div>
        </div>
    );
};
