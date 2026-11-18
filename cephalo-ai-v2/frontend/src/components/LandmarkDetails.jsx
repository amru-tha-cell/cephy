
import React from "react";

const LandmarkDetails = ({
  point,
  index,
  totalLandmarks = 19,
  onReset,
}) => {
  if (!point || index === null || index === undefined) {
    return (
      <section className="details-panel">
        <div className="details-empty">
          <div className="details-empty-icon">◎</div>
          <h3>No landmark selected</h3>
          <p>Select a landmark to inspect its prediction details.</p>
        </div>
      </section>
    );
  }

  const name =
    point.name ||
    point.landmark_name ||
    `Landmark ${index + 1}`;

  const confidence =
    point.confidence ?? point.reliability ?? null;

  const uncertainty =
    point.uncertainty ?? point.uncertainty_px ?? null;

  const corrected =
    point.corrected === true ||
    point.status === "corrected" ||
    point.is_manual === true;

  const originalX =
    point.initial_x ?? point.original_x ?? null;

  const originalY =
    point.initial_y ?? point.original_y ?? null;

  const formatValue = (value, decimals = 2) => {
    if (value === null || value === undefined) return "—";

    const number = Number(value);

    return Number.isFinite(number)
      ? number.toFixed(decimals)
      : "—";
  };

  const formatConfidence = (value) => {
    if (value === null || value === undefined) return "—";

    const number = Number(value);

    if (!Number.isFinite(number)) return "—";

    return `${(number <= 1 ? number * 100 : number).toFixed(1)}%`;
  };

  return (
    <section className="details-panel">
      <div className="details-heading">
        <div>
          <span className="details-eyebrow">
            LANDMARK {String(index + 1).padStart(2, "0")} / {totalLandmarks}
          </span>

          <h2>{name}</h2>
        </div>

        <span
          className={`details-status ${
            corrected ? "corrected" : "detected"
          }`}
        >
          {corrected ? "Manually corrected" : "AI detected"}
        </span>
      </div>

      <div className="details-section">
        <h3>Prediction information</h3>

        <div className="details-metric">
          <div>
            <span>Model confidence</span>
            <strong>{formatConfidence(confidence)}</strong>
          </div>

          <div>
            <span>Uncertainty</span>
            <strong>
              {uncertainty !== null
                ? `${formatValue(uncertainty)} px`
                : "—"}
            </strong>
          </div>
        </div>
      </div>

      <div className="details-section">
        <h3>Current coordinates</h3>

        <div className="coordinate-grid">
          <div className="coordinate-card">
            <span>X coordinate</span>
            <strong>{formatValue(point.x)} px</strong>
          </div>

          <div className="coordinate-card">
            <span>Y coordinate</span>
            <strong>{formatValue(point.y)} px</strong>
          </div>
        </div>
      </div>

      {(originalX !== null || originalY !== null) && (
        <div className="details-section">
          <h3>Original AI prediction</h3>

          <div className="coordinate-grid">
            <div className="coordinate-card">
              <span>Original X</span>
              <strong>{formatValue(originalX)} px</strong>
            </div>

            <div className="coordinate-card">
              <span>Original Y</span>
              <strong>{formatValue(originalY)} px</strong>
            </div>
          </div>
        </div>
      )}

      <div className="details-footer">
        <p>
          {corrected
            ? "This landmark has been manually adjusted."
            : "Drag this marker on the X-ray to correct its position."}
        </p>

        {corrected && onReset && (
          <button
            type="button"
            className="reset-landmark-button"
            onClick={() => onReset(index)}
          >
            Reset landmark
          </button>
        )}
      </div>
    </section>
  );
};

export default LandmarkDetails;
