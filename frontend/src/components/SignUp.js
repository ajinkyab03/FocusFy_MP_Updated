import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import bg from './assets/bg.mp4';

function SignUp() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignup = (e) => {
    e.preventDefault();
    axios
      .post("http://localhost:3001/signup", { name, email, password })
      .then((result) => {
        if (result.status === 201) {
          navigate("/login");
        }
      })
      .catch((err) => {
        if (err.response && err.response.status === 400) {
          window.alert("Email already exists. Please use a different email.");
        } else {
          console.log(err);
        }
      });
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gray-100">
      <video
        className="absolute top-0 left-0 w-full h-full object-cover"
        autoPlay
        loop
        muted
      >
        <source src={bg} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div className="bg-white bg-opacity-80 p-8 rounded-lg shadow-lg w-full max-w-md z-10">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
          Create Your Account
        </h2>
        <form onSubmit={handleSignup}>
          <div className="mb-6">
            <label className="block text-gray-700 text-lg font-semibold mb-2">
              Full Name
            </label>
            <input
              type="text"
              placeholder="Enter your full name"
              className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring focus:ring-blue-500 focus:outline-none"
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-lg font-semibold mb-2">
              Email Address
            </label>
            <input
              type="email"
              placeholder="Enter your email"
              className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring focus:ring-blue-500 focus:outline-none"
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-lg font-semibold mb-2">
              Password
            </label>
            <input
              type="password"
              placeholder="Enter your password"
              className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring focus:ring-blue-500 focus:outline-none"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded-lg text-lg font-semibold hover:bg-blue-600 transition duration-300"
          >
            Sign Up
          </button>
        </form>

        <p className="text-center text-gray-600 mt-6">
          Already have an account?{" "}
          <a href="/login" className="text-blue-500 font-bold hover:underline">
            Login
          </a>
        </p>
      </div>
    </div>
  );
}

export default SignUp;
