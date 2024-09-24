import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { HexColorPicker, HexColorInput } from 'react-colorful';

const MapMaker = () => {
  const navigate = useNavigate();
  const [gridSize, setGridSize] = useState({ width: 20, height: 15 });
  const [tileSize, setTileSize] = useState(30);
  const [selectedColor, setSelectedColor] = useState('#000000');
  const [isErasing, setIsErasing] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [mapName, setMapName] = useState('');
  const [layers, setLayers] = useState(() => {
    const storedLayers = localStorage.getItem('mapLayers');
    return storedLayers ? JSON.parse(storedLayers) : [
      { id: 1, name: 'Background', visible: true, data: [] },
      { id: 2, name: 'Middleground', visible: true, data: [] },
      { id: 3, name: 'Foreground', visible: true, data: [] },
    ];
  });
  const [activeLayer, setActiveLayer] = useState(1);
  const canvasRef = useRef(null);

  useEffect(() => {
    renderLayers();
  }, [layers, gridSize, tileSize]);

  useEffect(() => {
    localStorage.setItem('mapLayers', JSON.stringify(layers));
  }, [layers]);

  const drawGrid = (ctx) => {
    ctx.strokeStyle = '#ccc';
    for (let x = 0; x <= gridSize.width; x++) {
      ctx.beginPath();
      ctx.moveTo(x * tileSize, 0);
      ctx.lineTo(x * tileSize, gridSize.height * tileSize);
      ctx.stroke();
    }
    for (let y = 0; y <= gridSize.height; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * tileSize);
      ctx.lineTo(gridSize.width * tileSize, y * tileSize);
      ctx.stroke();
    }
  };

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / tileSize);
    const y = Math.floor((e.clientY - rect.top) / tileSize);
    fillTile(x, y);
  };

  const handleMouseMove = (e) => {
    if (isDrawing) {
      handleCanvasClick(e);
    }
  };

  const fillTile = (x, y) => {
    const newLayers = layers.map(layer => {
      if (layer.id === activeLayer) {
        const tileIndex = layer.data.findIndex(tile => tile.x === x && tile.y === y);
        if (isErasing) {
          if (tileIndex > -1) {
            layer.data.splice(tileIndex, 1);
          }
        } else {
          const newTile = { x, y, color: selectedColor };
          if (tileIndex > -1) {
            layer.data[tileIndex] = newTile;
          } else {
            layer.data.push(newTile);
          }
        }
      }
      return layer;
    });
    setLayers(newLayers);
  };

  const renderLayers = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    layers.forEach(layer => {
      if (layer.visible) {
        layer.data.forEach(tile => {
          ctx.fillStyle = tile.color;
          ctx.fillRect(tile.x * tileSize, tile.y * tileSize, tileSize, tileSize);
        });
      }
    });
    
    drawGrid(ctx);
  };

  const handleSizeChange = (e) => {
    const { name, value } = e.target;
    setGridSize(prev => ({ ...prev, [name]: parseInt(value) }));
  };

  const toggleLayerVisibility = (layerId) => {
    setLayers(layers.map(layer =>
      layer.id === layerId ? { ...layer, visible: !layer.visible } : layer
    ));
  };

  const saveMap = async () => {
    if (!mapName) {
      alert('Please enter a map name before saving.');
      return;
    }

    const mapData = {
      name: mapName,
      width: gridSize.width,
      height: gridSize.height,
      layers: layers
    };

    try {
      const response = await fetch('/api/game/save-map/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mapData),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      alert(`Map saved successfully! Map ID: ${result.map_id}`);
    } catch (error) {
      console.error('Error saving map:', error);
      alert('Failed to save map. Please try again.');
    }
  };

  return (
    <div className="map-maker">
      <h2>Map Maker</h2>
      <button onClick={() => navigate('/menu')}>Back to Menu</button>
      <div className="controls">
        <label>
          Width:
          <input
            type="number"
            name="width"
            value={gridSize.width}
            onChange={handleSizeChange}
            min="1"
            max="50"
          />
        </label>
        <label>
          Height:
          <input
            type="number"
            name="height"
            value={gridSize.height}
            onChange={handleSizeChange}
            min="1"
            max="50"
          />
        </label>
        <div className="color-picker-container">
          <button 
            className="color-preview" 
            style={{ backgroundColor: selectedColor }}
            onClick={() => setShowColorPicker(!showColorPicker)}
          ></button>
          {showColorPicker && (
            <div className="color-picker-popup">
              <HexColorPicker color={selectedColor} onChange={setSelectedColor} />
              <HexColorInput color={selectedColor} onChange={setSelectedColor} />
            </div>
          )}
        </div>
        <button onClick={() => setIsErasing(!isErasing)}>
          {isErasing ? 'Draw' : 'Erase'}
        </button>
        <input
          type="text"
          value={mapName}
          onChange={(e) => setMapName(e.target.value)}
          placeholder="Enter map name"
        />
        <button onClick={saveMap}>Save Map</button>
      </div>
      <div className="layers-control">
        {layers.map(layer => (
          <div key={layer.id}>
            <input
              type="radio"
              id={`layer-${layer.id}`}
              name="active-layer"
              checked={activeLayer === layer.id}
              onChange={() => setActiveLayer(layer.id)}
            />
            <label htmlFor={`layer-${layer.id}`}>{layer.name}</label>
            <input
              type="checkbox"
              checked={layer.visible}
              onChange={() => toggleLayerVisibility(layer.id)}
            />
          </div>
        ))}
      </div>
      <canvas
        ref={canvasRef}
        width={gridSize.width * tileSize}
        height={gridSize.height * tileSize}
        onClick={handleCanvasClick}
        onMouseDown={() => setIsDrawing(true)}
        onMouseUp={() => setIsDrawing(false)}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setIsDrawing(false)}
      ></canvas>
    </div>
  );
};

export default MapMaker;