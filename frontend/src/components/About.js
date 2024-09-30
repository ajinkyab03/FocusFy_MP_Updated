import React from 'react';
import Card from './Card';
import './style2.css';


export default function About() {
  return (
    <div>
      <h1>About FocusFy</h1>
      <h2>Our Mission:</h2>
      <p>"To empower students by enhancing their focus and productivity through
         real-time analysis of their study environment, providing actionable 
         insights and personalized recommendations for improved academic performance."</p>

         <h2>FocusFy Contributors</h2>
         <Card
         imgSrc='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSixcmQsARbTtwpySN--xqSmWg_p2yTCYv80A&s'
         name='Shravani'
         />

         <Card
         imgSrc='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYAcCQTp6jMR-GP6N8-lpccALnMtVyeX6LqA&s'
         name='Anjali'
         />

         <Card
         imgSrc='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRQ_2oII-AssPFNOvcLQ6ecJ6ZWQlUbKU3j8w&s'
         name='Ajinkya'
         />

         
         <div>
         <footer className="footer">
      <p>&copy; {new Date().getFullYear()} FocusFy. All rights reserved.</p>
    </footer>
         </div>

    </div>


  )
}
