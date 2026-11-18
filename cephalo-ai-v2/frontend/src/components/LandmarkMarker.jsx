
import React from "react";

const LandmarkMarker = ({
  point,
  index,
  selected,
  hovered,
  onSelect,
  onHover,
  onPointerDown,
}) => {
  if (!point) return null;

  const x = Number(point.x);
  const y = Number(point.y);

  if (!Number.isFinite(x) || !Number.isFinite(y)) {
    return null;
  }

  const isCorrected =
    point.corrected === true ||
    point.status === "corrected" ||
    point.is_manual === true;

  const color = isCorrected ? "#f2a93b" : "#43d9c9";

  const radius = selected ? 11 : hovered ? 9 : 7;

  return (
    <g
      transform={`translate(${x}, ${y})`}
      style={{ cursor: "grab" }}
      onPointerEnter={() => onHover(index)}
      onPointerLeave={() => onHover(null)}
      onPointerDown={(event) => {
        event.stopPropagation();
        onSelect(index);
        onPointerDown?.(event, index);
      }}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(index);
      }}
    >
      {/* Outer glow */}
      {(hovered || selected) && (
        <circle
          r={radius + 9}
          fill={color}
          opacity="0.13"
          style={{ pointerEvents: "none" }}
        />
      )}

      {/* Highlight ring */}
      {(hovered || selected) && (
        <circle
          r={radius + 4}
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          opacity="0.9"
          style={{ pointerEvents: "none" }}
        />
      )}

      {/* Main marker */}
      <circle
        r={radius}
        fill={color}
        stroke="#0a0e17"
        strokeWidth="2"
        style={{ pointerEvents: "none" }}
      />

      {/* Center point */}
      <circle
        r="2"
        fill="#ffffff"
        style={{ pointerEvents: "none" }}
      />

      {/* Invisible larger hit area for easier interaction */}
      <circle
        r="17"
        fill="transparent"
        stroke="transparent"
      />
    </g>
  );
};

export default LandmarkMarker;
