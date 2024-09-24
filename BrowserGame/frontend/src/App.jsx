import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Menu from './components/Menu';
import Game from './components/Game';
import MapMaker from './components/MapMaker';
import Host from './components/Host';

function App() {
  return (
    <Router>
      <div className="App" style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
        <Routes>
          <Route path="/" element={<Menu />} />
		  <Route path="/menu" element={<Menu />} />
          <Route path="/game" element={<Game />} />
          <Route path="/map-maker" element={<MapMaker />} />
          <Route path="/host" element={<Host />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;