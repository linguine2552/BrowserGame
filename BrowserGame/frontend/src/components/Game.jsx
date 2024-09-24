import React, { useRef, useEffect, useState, useCallback } from 'react';
import Player from './Player';
import Landscape from './Landscape';
import DustAnimation from './DustAnimation';

const Game = () => {
  const containerRef = useRef(null);
  const socketRef = useRef(null);
  const initializedRef = useRef(false);
  const animationFrameRef = useRef(null);

  const [gameState, setGameState] = useState({
    players: {},
  });

  const [dustAnimations, setDustAnimations] = useState([]);
  const lastPlayerPositionRef = useRef({ x: 0, y: 0 });
  const lastDirectionRef = useRef(null);

  const [playerId, setPlayerId] = useState(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });
  const [mapData, setMapData] = useState(null);

  const [localPlayerState, setLocalPlayerState] = useState({ x: 0, y: 0, speed: 0, angle: 0 });
  const lastServerUpdateTimeRef = useRef(0);
  const serverUpdateIntervalRef = useRef(5); // 50ms

  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [playerMousePosition, setPlayerMousePosition] = useState({ x: 0, y: 0 });
  const playerRef = useRef(null);

  const [playerMovement, setPlayerMovement] = useState({
    left: false,
    right: false,
    guard: false,
    running: false,
	crouching: false,
  });

  const lastUpdateTimeRef = useRef(0);
  const playerPositionRef = useRef({ x: 0, y: 0 });

  const GROUND_HEIGHT_RATIO = 0.05;
  const MOVE_SPEED = 30; // pixels per second

  const [playerSpeed, setPlayerSpeed] = useState(30);
  const TILE_ASPECT_RATIO = 1.5;
  const TILE_WIDTH_PERCENTAGE = 0.05;
  const BACKGROUND_COLOR = '#e79506';
  const [tileDimensions, setTileDimensions] = useState({ width: 0, height: 0 });
  const TILE_SIZE = 30;
  const MAP_WIDTH = 20;
  const MAP_HEIGHT = 15;

const convertToPixels = (tileX, tileY) => {
  return {
    x: tileX * TILE_SIZE,
    y: tileY * TILE_SIZE
  };
};
    useEffect(() => {
    const calculateTileDimensions = () => {
      const tileWidth = Math.floor(canvasSize.width * TILE_WIDTH_PERCENTAGE);
      const tileHeight = Math.floor(tileWidth / TILE_ASPECT_RATIO);
      setTileDimensions({ width: tileWidth, height: tileHeight });
    };

    calculateTileDimensions();
  }, [canvasSize]);
  
  const resizeCanvas = useCallback(() => {
    if (containerRef.current) {
      const { clientWidth, clientHeight } = containerRef.current;
      setCanvasSize({ width: clientWidth, height: clientHeight });
    }
  }, []);

  useEffect(() => {
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    return () => window.removeEventListener('resize', resizeCanvas);
  }, [resizeCanvas]);

  useEffect(() => {
    const initializeGame = async () => {
      if (initializedRef.current) return;
      initializedRef.current = true;

      try {
        const response = await fetch('/api/game/initialize/');
        const data = await response.json();
        console.log("Parsed data:", data);
        setPlayerId(data.player_id);
        setMapData(data.map);
      } catch (error) {
        console.error('Error initializing game:', error);
      }
    };

    initializeGame();
  }, []);

  useEffect(() => {
    if (!playerId) return;

    socketRef.current = new WebSocket(`ws://${window.location.hostname}:8000/ws/game/${playerId}/`);

    socketRef.current.onopen = () => {
      console.log('WebSocket connection established');
    };

    socketRef.current.onmessage = (event) => {
      try {
        const newGameState = JSON.parse(event.data);
        // console.log('Received game state:', newGameState);

        Object.entries(newGameState).forEach(([id, playerData]) => {
          console.log(`Player ${id} pivot points:`, playerData.pivot_points);
        });

        setGameState(prevState => ({
          ...prevState,
          players: newGameState,
        }));

        if (newGameState[playerId]) {
          playerPositionRef.current = {
            x: newGameState[playerId].x,
            y: newGameState[playerId].y,
          };
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socketRef.current.onclose = (event) => {
      console.log('WebSocket connection closed:', event);
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [playerId]);

const handleDirectionChange = useCallback(() => {
  const anklePoints = gameState.players[playerId].pivot_points;
  if (anklePoints && anklePoints.l_ankle && anklePoints.r_ankle) {
    const leftAnkleX = (anklePoints.l_ankle[0] * TILE_SIZE) + (localPlayerState.x * TILE_SIZE);
    const leftAnkleY = ((2 - anklePoints.l_ankle[1]) * TILE_SIZE) + ((MAP_HEIGHT - localPlayerState.y - 2) * TILE_SIZE);
    const rightAnkleX = (anklePoints.r_ankle[0] * TILE_SIZE) + (localPlayerState.x * TILE_SIZE);
    const rightAnkleY = ((2 - anklePoints.r_ankle[1]) * TILE_SIZE) + ((MAP_HEIGHT - localPlayerState.y - 2) * TILE_SIZE);

    setDustAnimations(prev => [
      ...prev,
      { id: Date.now(), x: leftAnkleX - 40, y: leftAnkleY + 39},
      { id: Date.now() + 1, x: rightAnkleX - 40, y: rightAnkleY + 39}
    ]);

    console.log('Dust animation positions:', {
      leftAnkle: { x: leftAnkleX, y: leftAnkleY },
      rightAnkle: { x: rightAnkleX, y: rightAnkleY }
    });
  }
}, [gameState, playerId, localPlayerState.x, localPlayerState.y]);

  const updatePlayerPosition = useCallback((deltaTime) => {
    if (!playerId || !gameState.players[playerId]) return;

    const serverPlayer = gameState.players[playerId];
    const currentSpeed = serverPlayer.speed;

    let newX = localPlayerState.x;
    const moveDistance = (currentSpeed / TILE_SIZE) * deltaTime;

    if (playerMovement.left) {
      newX = Math.max(0, newX - moveDistance);
    }
    if (playerMovement.right) {
      newX = Math.min(MAP_WIDTH - 1, newX + moveDistance);
    }

	if (playerMovement.running) {
	  const currentDirection = newX > lastPlayerPositionRef.current.x ? 'right' : 'left';
	  if (currentDirection !== lastDirectionRef.current && Math.abs(newX - lastPlayerPositionRef.current.x) > 0.01) {
		handleDirectionChange();
		lastDirectionRef.current = currentDirection;
	  }
	}

    lastPlayerPositionRef.current = { x: newX, y: localPlayerState.y };
    setLocalPlayerState(prev => ({ ...prev, x: newX, speed: currentSpeed }));

    if (Date.now() - lastServerUpdateTimeRef.current > serverUpdateIntervalRef.current) {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ 
          x: newX,
          running: playerMovement.running,
		  crouching: playerMovement.crouching
        }));
      }
      lastServerUpdateTimeRef.current = Date.now();
    }
  }, [playerId, gameState, playerMovement, localPlayerState]);

  const gameLoop = useCallback((timestamp) => {
    if (!lastUpdateTimeRef.current) {
      lastUpdateTimeRef.current = timestamp;
    }

    const deltaTime = (timestamp - lastUpdateTimeRef.current) / 1000;
    lastUpdateTimeRef.current = timestamp;

    updatePlayerPosition(deltaTime);

    animationFrameRef.current = requestAnimationFrame(gameLoop);
  }, [updatePlayerPosition]);

  useEffect(() => {
    if (gameState.players[playerId]) {
      const serverPlayer = gameState.players[playerId];
      setLocalPlayerState(prev => ({
        ...prev,
        x: serverPlayer.x,
        y: serverPlayer.y,
        speed: serverPlayer.speed,
        angle: serverPlayer.angle
      }));
    }
  }, [gameState, playerId]);

  useEffect(() => {
    animationFrameRef.current = requestAnimationFrame(gameLoop);
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [gameLoop]);

  const handleKeyDown = useCallback((e) => {
    switch (e.key.toLowerCase()) {
      case 'arrowleft':
      case 'a':
        setPlayerMovement(prev => ({ ...prev, left: true }));
        break;
      case 'arrowright':
      case 'd':
        setPlayerMovement(prev => ({ ...prev, right: true }));
        break;
      case 'arrowup':
      case ' ':
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ jump: true }));
        }
        break;
      case 'w':
        setPlayerMovement(prev => ({ ...prev, guard: true }));
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ guard: true }));
        }
        break;
      case 'shift':
        setPlayerMovement(prev => ({ ...prev, running: true }));
        break;
      case 'c':
        setPlayerMovement(prev => ({ ...prev, crouching: true }));
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ crouching: true }));
        }
        break;
    }
  }, []);

  const handleKeyUp = useCallback((e) => {
    switch (e.key.toLowerCase()) {
      case 'arrowleft':
      case 'a':
        setPlayerMovement(prev => ({ ...prev, left: false }));
        break;
      case 'arrowright':
      case 'd':
        setPlayerMovement(prev => ({ ...prev, right: false }));
        break;
      case 'w':
        setPlayerMovement(prev => ({ ...prev, guard: false }));
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ guard: false }));
        }
        break;
      case 'shift':
        setPlayerMovement(prev => ({ ...prev, running: false }));
        break;
      case 'c':
        setPlayerMovement(prev => ({ ...prev, crouching: false }));
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ crouching: false }));
        }
        break;
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [handleKeyDown, handleKeyUp]);

  const handleMouseMove = useCallback((e) => {
    if (playerRef.current && playerId) {
      const playerRect = playerRef.current.getBoundingClientRect();
      const newPlayerMousePosition = {
        x: e.clientX - playerRect.left,
        y: e.clientY - playerRect.top
      };
      setPlayerMousePosition(newPlayerMousePosition);

      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({
          player_mouse_position: newPlayerMousePosition
        }));
      }
    }
  }, [playerId]);

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [handleMouseMove]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: `${MAP_WIDTH * TILE_SIZE}px`, 
        height: `${MAP_HEIGHT * TILE_SIZE}px`, 
        overflow: 'hidden', 
        position: 'relative',
      }}
    >
      {mapData && (
        <Landscape
          worldData={mapData}
          tileSize={TILE_SIZE}
        />
      )}
      {Object.entries(gameState.players).map(([id, playerData]) => {
        const isLocalPlayer = id === playerId;
        const x = isLocalPlayer ? localPlayerState.x : playerData.x;
        const y = isLocalPlayer ? localPlayerState.y : playerData.y;
        const angle = isLocalPlayer ? localPlayerState.angle : playerData.angle;
        return (
          <Player
            key={id}
            x={x * TILE_SIZE}
            y={(MAP_HEIGHT - y - 2) * TILE_SIZE}
            width={TILE_SIZE}
            height={TILE_SIZE * 2}
            color={isLocalPlayer ? 'red' : 'blue'}
            pivotPoints={playerData.pivot_points}
            ref={isLocalPlayer ? playerRef : null}
            mouseX={isLocalPlayer ? playerMousePosition.x : null}
            angle={angle}
          />
        );
      })}
      {dustAnimations.map(dust => (
        <DustAnimation key={dust.id} x={dust.x} y={dust.y} />
      ))}
      {/* Debug info overlay */}
      <div style={{
        position: 'absolute',
        top: 10,
        left: 10,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        fontFamily: 'monospace'
      }}>
        <div>Player Mouse: X: {playerMousePosition.x.toFixed(2)}, Y: {playerMousePosition.y.toFixed(2)}</div>
        <div>Player Angle: {localPlayerState.angle.toFixed(2)}</div>
        <div>Crouching: {playerMovement.crouching ? 'Yes' : 'No'}</div>
      </div>
    </div>
  );
};

export default Game;