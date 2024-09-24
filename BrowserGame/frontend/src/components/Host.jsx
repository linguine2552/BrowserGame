import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Host = () => {
  const [maps, setMaps] = useState([]);
  const [selectedMap, setSelectedMap] = useState(null);
  const [hostName, setHostName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMaps();
  }, []);

  const fetchMaps = async () => {
    try {
      const response = await axios.get('/api/game/maps/');
      setMaps(response.data);
    } catch (error) {
      console.error('Error fetching maps:', error);
    }
  };

  const handleMapSelect = (map) => {
    setSelectedMap(map);
  };

  const createLobby = async () => {
    if (!selectedMap || !hostName) return;

    try {
      const response = await axios.post('/api/game/create-lobby/', { 
        map_id: selectedMap.id,
        host_name: hostName
      });
      const { lobby_code, host_id, map_data } = response.data;
      
      // Navigate to Lobby component with the new route and map data
      navigate(`/lobby/${lobby_code}`, { 
        state: { 
          playerId: host_id, 
          playerName: hostName,
          isHost: true,
          mapData: map_data
        } 
      });
    } catch (error) {
      console.error('Error creating lobby:', error);
    }
  };

  return (
    <div className="host-container">
      <h1>Host a Game</h1>
      
      <div className="map-selection">
        <h2>Select a Map</h2>
        <ul>
          {maps.map((map) => (
            <li 
              key={map.id} 
              onClick={() => handleMapSelect(map)}
              className={selectedMap && selectedMap.id === map.id ? 'selected' : ''}
            >
              {map.name} ({map.width}x{map.height})
            </li>
          ))}
        </ul>
      </div>

      <div className="host-name-input">
        <h2>Enter Your Name</h2>
        <input 
          type="text" 
          value={hostName} 
          onChange={(e) => setHostName(e.target.value)}
          placeholder="Enter your name"
        />
      </div>

      {selectedMap && hostName && (
        <div className="lobby-creation">
          <button onClick={createLobby}>Create Lobby with Selected Map</button>
        </div>
      )}
    </div>
  );
};

export default Host;