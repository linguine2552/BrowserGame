import React from 'react';

const GridOverlay = ({ width, height, tileSize }) => {
  const gridStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    width: `${width}px`,
    height: `${height}px`,
    pointerEvents: 'none',
  };

  const lineStyle = {
    stroke: 'rgba(255, 0, 0, 0.5)',
    strokeWidth: '1',
  };

  const lines = [];
  for (let x = 0; x <= width; x += tileSize) {
    lines.push(<line key={`v${x}`} x1={x} y1={0} x2={x} y2={height} style={lineStyle} />);
  }
  for (let y = 0; y <= height; y += tileSize) {
    lines.push(<line key={`h${y}`} x1={0} y1={y} x2={width} y2={y} style={lineStyle} />);
  }

  return (
    <svg style={gridStyle}>
      {lines}
    </svg>
  );
};

export default GridOverlay;