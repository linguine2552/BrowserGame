import React, { forwardRef, useState, useEffect } from 'react';
import Sword from './Sword';

const LINE_THICKNESS = 0.15;
const POINT_SIZE = 0.06;
const BOUNDARY_STROKE_WIDTH = 0.02;
const MIN_SWORD_LENGTH = 1.6;
const MAX_SWORD_LENGTH = 1.6;

const Player = forwardRef(({ id, x, y, width, height, color = 'black', pivotPoints, mouseX, onCollisionShapeChange, isHit, angle }, ref) => {
  const [collisionShape, setCollisionShape] = useState(null);
  if (!pivotPoints) {
    console.warn('Pivot points not provided for player');
    return null;
  }

  const flipY = y => y;

  const drawLine = (start, end) => {
    if (!pivotPoints[start] || !pivotPoints[end]) return '';
    const [startX, startY] = pivotPoints[start];
    const [endX, endY] = pivotPoints[end];
    return `M${startX},${flipY(startY)} L${endX},${flipY(endY)}`;
  };

  const renderHead = (() => {
    if (!pivotPoints.neck || !pivotPoints.top_head) return null;
    const [neckX, neckY] = pivotPoints.neck;
    const [topHeadX, topHeadY] = pivotPoints.top_head;
    const radius = Math.abs(topHeadY - neckY) / 2;
    const centerX = neckX;
    const centerY = (neckY + topHeadY) / 2;
    return (
      <circle 
        cx={centerX} 
        cy={flipY(centerY)} 
        r={radius} 
        fill={color} 
        stroke={color} 
        strokeWidth={LINE_THICKNESS} 
      />
    );
  })();

  const bodyPath = [
    // Body
    drawLine('neck', 'spine_01'),
    drawLine('spine_01', 'spine_02'),
    drawLine('spine_02', 'pelvis'),

    // Arms
    drawLine('neck', 'l_elbow'),
    drawLine('l_elbow', 'l_hand'),
    drawLine('neck', 'r_elbow'),
    drawLine('r_elbow', 'r_hand'),

    // Legs
    drawLine('pelvis', 'l_knee'),
    drawLine('l_knee', 'l_ankle'),
    drawLine('l_ankle', 'l_toe'),
    drawLine('pelvis', 'r_knee'),
    drawLine('r_knee', 'r_ankle'),
    drawLine('r_ankle', 'r_toe'),
  ].join(' ');

  const renderPoint = (key, point) => {
    if (!point) return null;
    const [cx, cy] = point;
    return (
      <circle
        key={key}
        cx={cx}
        cy={flipY(cy)}
        r={POINT_SIZE}
        fill={color} 
      />
    );
  };

  const renderSword = () => {
    if (!pivotPoints.r_hand || !pivotPoints.sword_tip) return null;
    const [handX, handY] = pivotPoints.r_hand;
    const [tipX, tipY] = pivotPoints.sword_tip;

    const unclampedLength = Math.sqrt(Math.pow(tipX - handX, 2) + Math.pow(tipY - handY, 2));

    const swordLength = Math.max(MIN_SWORD_LENGTH, Math.min(MAX_SWORD_LENGTH, unclampedLength));

    const swordAngle = Math.atan2(tipY - handY, tipX - handX);

    const clampedTipX = handX + Math.cos(swordAngle) * swordLength;
    const clampedTipY = handY + Math.sin(swordAngle) * swordLength;

    return (
      <g>
        <g transform={`translate(${handX}, ${flipY(handY)}) rotate(${swordAngle * 180 / Math.PI})`}>
          <Sword 
            color={color} 
            length={swordLength} 
            mouseX={mouseX} 
            onCollisionShapeChange={handleCollisionShapeChange}
          />
          {/* Render collision shape */}
          {collisionShape && (
            <path
              d={collisionShape}
              fill="rgba(255, 0, 0, 0.3)"
              stroke={color}
              strokeWidth={0.01}
            />
          )}
        </g>

        {/* Small circle at tip for hit detection */}
        <circle
          cx={clampedTipX}
          cy={flipY(clampedTipY)}
          r={POINT_SIZE * 0.6}
          fill={color}
        />
      </g>
    );
  };

  const handleCollisionShapeChange = (newShape) => {
    setCollisionShape(newShape);
    
    const worldCollisionShape = {
      left: x + newShape.left,
      right: x + newShape.right,
      top: y + newShape.top,
      bottom: y + newShape.bottom
    };
    
    onCollisionShapeChange(worldCollisionShape);

    setTimeout(() => {
      setCollisionShape(null);
      onCollisionShapeChange(null);
    }, 500);
  };

  return (
    <div
      ref={ref}
      style={{
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        width: `${width}px`,
        height: `${height}px`,
      }}
    >
      <svg 
        width={width} 
        height={height} 
        viewBox="0 0 1 2"
        preserveAspectRatio="none"
        style={{
          overflow: 'visible',
        }}
      >
        {/* acceleration tilt */}
        <g transform={`rotate(${angle} 0.5 1)`}>
          {/* debug collision box */}
          <rect 
            x={BOUNDARY_STROKE_WIDTH / 2}
            y={BOUNDARY_STROKE_WIDTH / 2}
            width={1 - BOUNDARY_STROKE_WIDTH}
            height={2 - BOUNDARY_STROKE_WIDTH}
            fill={isHit ? 'rgba(255, 0, 0, 0.5)' : 'none'} 
            stroke={color} 
            strokeWidth={BOUNDARY_STROKE_WIDTH} 
          />

          {/* head */}
          {renderHead}

          {/* body */}
          <path d={bodyPath} stroke={color} strokeWidth={LINE_THICKNESS} fill="none" />
          {Object.entries(pivotPoints)
            .filter(([key]) => key !== 'r_shoulder' && key !== 'top_head')
            .map(([key, point]) => renderPoint(key, point))}

          {/* sword */}
          {renderSword()}
        </g>
      </svg>
    </div>
  );
});

export default Player;