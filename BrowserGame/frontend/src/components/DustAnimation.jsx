import React, { useState, useEffect } from 'react';

const DustAnimation = ({ x, y }) => {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  const sprites = [
    '/dust01.png',
    '/dust02.png',
    '/dust03.png'
  ];

  useEffect(() => {
    const animationInterval = setInterval(() => {
      setCurrentFrame((prevFrame) => {
        if (prevFrame >= sprites.length - 1) {
          clearInterval(animationInterval);
          setIsVisible(false);
          return prevFrame;
        }
        return prevFrame + 1;
      });
    }, 100); // change frame every 100ms

    return () => clearInterval(animationInterval);
  }, []);

  if (!isVisible) return null;

  return (
    <img
      src={sprites[currentFrame]}
      style={{
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        width: '30px',
        height: '30px',
        pointerEvents: 'none',
      }}
      alt="Dust"
    />
  );
};

export default DustAnimation;