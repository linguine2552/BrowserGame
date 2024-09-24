import React from 'react';

const Sword = ({ color = 'silver', length, mouseX }) => {
  const strokeWidth = 0.04;
  const edgeWidth = 0.01;
  const handleLength = 0.04;
  const hiltRadius = 0.1;
  const guardLength = 0.2;
  
  const scaleX = 1;

  return (
    <g transform={`scale(${scaleX}, 1)`}>
      {/* Handle (at the origin) */}
      <line
        x1={0}
        y1={0}
        x2={handleLength}
        y2={0}
        stroke="saddlebrown"
        strokeWidth={strokeWidth * 2}
      />

      {/* Hilt (semicircle just after the handle) */}
      <path
        d={`M ${handleLength} ${-hiltRadius} A ${hiltRadius} ${hiltRadius} 0 0 1 ${handleLength} ${hiltRadius}`}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth * 3.3}
      />

      {/* Cross Guard (lines extending from the hilt) */}
      <line
        x1={handleLength}
        y1={-0.25}
        x2={handleLength}
        y2={0.25}
        stroke={color}
        strokeWidth={strokeWidth * 1}
      />

      {/* Main Blade (straight line) */}
      <line
        x1={handleLength}
        y1={0}
        x2={length}
        y2={0}
        stroke={color}
        strokeWidth={strokeWidth}
      />

      {/* Top Edge (logarithmic curve flanking the main blade outward) */}
      <path
        d={`M ${handleLength} -${edgeWidth} C ${(handleLength + length) / 9} -0.001, ${(handleLength + length) * -0.65} -0.05, ${length} -${edgeWidth}`}
        fill="none"
        stroke={color}
        strokeWidth={edgeWidth + 0.015}
      />

      {/* Bottom Edge (logarithmic curve flanking the main blade outward) */}
      <path
        d={`M ${handleLength} ${edgeWidth} C ${(handleLength + length) / 9} 0.001, ${(handleLength + length) * -0.65} 0.05, ${length} ${edgeWidth}`}
        fill="none"
        stroke={color}
        strokeWidth={edgeWidth + 0.015}
      />
    </g>
  );
};

export default Sword;