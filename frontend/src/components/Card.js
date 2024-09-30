import React from 'react';
 import './style2.css';  // Assuming the CSS file is named Card.css

export default function Card({ imgSrc, name }) {
  return (
    <div className="card">
      <img src={imgSrc} alt={name} />
      <h1>{name}</h1>
    </div>
  );
}
