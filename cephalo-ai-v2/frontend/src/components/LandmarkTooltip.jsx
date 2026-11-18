
import React from "react";

const LandmarkTooltip = ({ point, index, position }) => {
  if (!point || !position) return null;

  const landmarkName =
    point.name || point.landmark_name || `Landmark ${index + 1}`;

  const confidence =
    point.confidence ?? point.reliability ?? null;

  const uncertainty =
    point.uncertainty ?? point.uncertainty_px ?? null;

  const isCorrected =
    point.corrected === true ||
    point.status === "corrected" ||
    point.is_manual === true;

  const formatNumber = (value, decimals = 2) => {
    const number = Number(value);

    return Number.isFinite(number)
      ? number.toFixed(decimals)
      : "—";
  };

  const formatConfidence = (value) => {
    if (value === null || value === undefined) return "—";

    const number = Number(value);

    if (!Number.isFinite(number)) return "—";

    // Backend confidence may be represented as either
    // a fraction (0 to 1) or a percentage (0 to 100).
    const percentage = number <= 1 ? number * 100 : number;

    return `${percentage.toFixed(1)}%`;
  };

  return (
    <div
      className="landmark-tooltip"
      style={{
        left: position.x,
        top: position.y,
      }}
    >
      <div className="tooltip-header">
        <div>
          <span className="tooltip-index">
            LANDMARK {String(index + 1).padStart(2, "0")}
          </span>

          <h3>{landmarkName}</h3>
        </div>

        <span
          className={`tooltip-status ${
            isCorrected ? "corrected" : "detected"
          }`}
        >
          {isCorrected ? "Corrected" : "AI detected"}
        </span>
      </div>

      <div className="tooltip-divider" />

      <div className="tooltip-grid">
        <div className="tooltip-item">
          <span>X COORDINATE</span>
          <strong>{formatNumber(point.x)} px</strong>
        </div>

        <div className="tooltip-item">
          <span>Y COORDINATE</span>
          <strong>{formatNumber(point.y)} px</strong>
        </div>

        <div className="tooltip-item">
          <span>MODEL CONFIDENCE</span>
          <strong>
            {formatConfidence(confidence)}
          </strong>
        </div>

        <div className="tooltip-item">
          <span>UNCERTAINTY</span>
          <strong>
            {uncertainty !== null && uncertainty !== undefined
              ? `${formatNumber(uncertainty)} px`
              : "—"}
          </strong>
        </div>
      </div>

      <div className="tooltip-footer">
        Hover over another marker to inspect its prediction
      </div>
    </div>
  );
};

export default LandmarkTooltip;
