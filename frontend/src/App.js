// import React, { useState, useEffect } from "react";
// import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
// import Login from "./components/Login";
// import SignUp from "./components/SignUp";
// import { Navbar } from "./components/Navbar";
// import WebcamControl from './components/WebcamControl';
// import axios from "axios";
// import QuotesGenerator from "./components/QuotesGenerator";

// function App() {
//   const [isLoggedIn, setIsLoggedIn] = useState(false);
//   const [user, setUser] = useState({ email: "", name: "" });

//   useEffect(() => {
//     axios.get('http://localhost:3001/user', { withCredentials: true })
//       .then(response => {
//         if (response.data.user) {
//           setIsLoggedIn(true);
//           setUser({
//             email: response.data.user.email,
//             name: response.data.user.name
//           });
//         } else {
//           setIsLoggedIn(false);
//         }
//       })
//       .catch(() => setIsLoggedIn(false));
//   }, []);

//   return (
//     <div>
//       <BrowserRouter>
//         <Navbar isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />
//         <Routes>
//           <Route path="/" element={isLoggedIn ? <Navigate to="/home" /> : <Navigate to="/login" />} />
//           <Route path="/home" element={isLoggedIn ? <WebcamControl user={user} /> : <Navigate to="/login" />} />
//           <Route path="/quote" element={isLoggedIn ? <QuotesGenerator/> : <Navigate to="/login"/>}/>
//           <Route path="/login" element={isLoggedIn ? <Navigate to="/home" /> : <Login setIsLoggedIn={setIsLoggedIn} setUser={setUser} />} />
//           <Route path="/signup" element={isLoggedIn ? <Navigate to="/home" /> : <SignUp setIsLoggedIn={setIsLoggedIn} />} />
//           {/* <Route path="/timetable" element={isLoggedIn ? <Navigate to="/home" /> : <SignUp setIsLoggedIn={setIsLoggedIn} />} /> */}

//         </Routes>
//       </BrowserRouter>
//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import { Navbar } from "./components/Navbar";
import WebcamControl from './components/WebcamControl';
import axios from "axios";
import QuotesGenerator from "./components/QuotesGenerator";
import About from "./components/About";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState({ email: "", name: "" });

  useEffect(() => {
    axios.get('http://localhost:3001/user', { withCredentials: true })
      .then(response => {
        if (response.data.user) {
          setIsLoggedIn(true);
          setUser({
            email: response.data.user.email,
            name: response.data.user.name
          });
        } else {
          setIsLoggedIn(false);
        }
      })
      .catch(() => setIsLoggedIn(false));
  }, []);

  console.log("Is Logged In:", isLoggedIn); // Debugging line

  return (
    <div>
      <BrowserRouter>
        <Navbar isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />
        <Routes>
          <Route path="/" element={isLoggedIn ? <Navigate to="/home" /> : <Navigate to="/login" />} />
          <Route path="/home" element={isLoggedIn ? <WebcamControl user={user} /> : <Navigate to="/login" />} />
          <Route path="/quote" element={<QuotesGenerator/>} />
          <Route path="/login" element={isLoggedIn ? <Navigate to="/home" /> : <Login setIsLoggedIn={setIsLoggedIn} setUser={setUser} />} />
          <Route path="/signup" element={isLoggedIn ? <Navigate to="/home" /> : <SignUp setIsLoggedIn={setIsLoggedIn} />} />
          <Route path="/about" element={<About/>} />

        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
