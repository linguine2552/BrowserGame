import React from 'react';
import { useNavigate } from 'react-router-dom';

const Menu = () => {
  const navigate = useNavigate();

  return (
    <div className="menu">
      <h1>NOS</h1>
      <div className="button-container">
        <button onClick={() => navigate('/host')}>Host Game</button>
        <button onClick={() => navigate('/game')}>Join Game</button>
        <button onClick={() => navigate('/map-maker')}>Map Maker</button>
      </div>
    </div>
  );
};

export default Menu;