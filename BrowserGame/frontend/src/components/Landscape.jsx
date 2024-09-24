import React, { useRef, useEffect } from 'react';

const Landscape = ({ worldData, tileSize }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!worldData) {
      console.log('Missing world data:', worldData);
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) {
      console.error('Canvas ref is null');
      return;
    }

    const ctx = canvas.getContext('2d');
	ctx.imageSmoothingEnabled = false;
    const { width, height, tiles } = worldData;

    console.log('World data:', { width, height, tileCount: tiles.length, tileSize });

    canvas.width = width * tileSize;
    canvas.height = height * tileSize;

    console.log('Canvas dimensions:', { width: canvas.width, height: canvas.height });

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    tiles.forEach(tile => {
      ctx.fillStyle = tile.color;
      ctx.fillRect(
        tile.x * tileSize,
        tile.y * tileSize,
        tileSize,
        tileSize
      );

      ctx.strokeStyle = 'black';
      ctx.lineWidth = 1;
      ctx.strokeRect(
        tile.x * tileSize,
        tile.y * tileSize,
        tileSize,
        tileSize
      );
    });

    console.log('Landscape rendered successfully');
  }, [worldData, tileSize]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
      }}
    />
  );
};

export default Landscape;