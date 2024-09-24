import React, { useState, useEffect, useRef } from 'react';

const Viewport = ({ children, playerX, playerY, mapWidth, mapHeight, viewportWidth, viewportHeight }) => {
  const [zoom, setZoom] = useState(1);
  const viewportRef = useRef(null);

  useEffect(() => {
    const handleWheel = (e) => {
      e.preventDefault();
      setZoom(prevZoom => {
        const zoomSpeed = 0.1;
        const newZoom = Math.max(0.5, Math.min(2, prevZoom * (1 - Math.sign(e.deltaY) * zoomSpeed)));
        return newZoom;
      });
    };

    const viewport = viewportRef.current;
    if (viewport) {
      viewport.addEventListener('wheel', handleWheel, { passive: false });
    }

    return () => {
      if (viewport) {
        viewport.removeEventListener('wheel', handleWheel);
      }
    };
  }, []);

  // Calculate the scaled dimensions
  const scaledWidth = viewportWidth / zoom;
  const scaledHeight = viewportHeight / zoom;

  // Calculate the position to center on the player
  let centerX = playerX - scaledWidth / 2;
  let centerY = playerY - scaledHeight / 2;

  // Clamp the center position to prevent showing areas outside the map
  centerX = Math.max(0, Math.min(mapWidth - scaledWidth, centerX));
  centerY = Math.max(0, Math.min(mapHeight - scaledHeight, centerY));

  return (
    <div
      ref={viewportRef}
      style={{
        width: `${viewportWidth}px`,
        height: `${viewportHeight}px`,
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      <div
        style={{
          transform: `scale(${zoom})`,
          transformOrigin: 'top left',
          width: `${mapWidth}px`,
          height: `${mapHeight}px`,
          position: 'absolute',
          left: `${-centerX * zoom}px`,
          top: `${-centerY * zoom}px`,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export default Viewport;