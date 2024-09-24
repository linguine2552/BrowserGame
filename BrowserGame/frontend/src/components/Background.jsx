import React from 'react';

const Background = ({ width, height, color }) => {
  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: `${width}px`,
        height: `${height}px`,
        backgroundColor: color,
      }}
    />
  );
};

export default Background;