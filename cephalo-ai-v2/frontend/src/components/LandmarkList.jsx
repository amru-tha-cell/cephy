
import React from "react";

const LandmarkList = ({
  landmarks = [],
  selectedIndex,
  onSelect,
}) => {
  const getConfidence = (point) => {
    const value = point.confidence ?? point.reliability;

    if (value === null || value === undefined) {
      return null;
    }

    const number = Number(value);

    if (!Number.isFinite(number)) return null;

    return number <= 1 ? number * 100 : number;
  };

  // Check the backend's manually_corrected field too.
  const isCorrected = (point) =>
    point.manually_corrected === true ||
    point.corrected === true ||
    point.status === "corrected" ||
    point.is_manual === true;

  const getLandmarkName = (point, index) =>
    point.name ||
    point.landmark_name ||
    `Landmark ${index + 1}`;

  // Count manually corrected landmarks.
  const correctedCount = landmarks.filter(isCorrected).length;

  return (
    <aside className="landmark-sidebar">
      <div className="sidebar-heading">
        <div>
          <h2>Landmarks</h2>
          <p>Cephalometric detection points</p>
        </div>

        <span
          className="landmark-count"
          title="Number of manually corrected landmarks"
        >
          {correctedCount}/19
        </span>
      </div>

      <div className="landmark-legend">
        <span>
          <i className="legend-dot ai-dot" />
          AI detected
        </span>

        <span>
          <i className="legend-dot corrected-dot" />
          Corrected
        </span>
      </div>

      <div className="landmark-list">
        {landmarks.length === 0 ? (
          <div className="landmark-empty">
            No landmarks detected yet.
          </div>
        ) : (
          landmarks.map((point, index) => {
            const confidence = getConfidence(point);
            const corrected = isCorrected(point);
            const selected = selectedIndex === index;

            return (
              <button
                type="button"
                key={point.id ?? index}
                className={`landmark-item ${
                  selected ? "selected" : ""
                }`}
                onClick={() => onSelect(index)}
              >
                <div className="landmark-item-main">
                  <span
                    className={`landmark-status-dot ${
                      corrected ? "corrected" : "detected"
                    }`}
                  />

                  <span className="landmark-name">
                    {String(index + 1).padStart(2, "0")}.
                    {" "}
                    {getLandmarkName(point, index)}
                  </span>
                </div>

                <div className="landmark-item-meta">
                  <span className="confidence-value">
                    {confidence !== null
                      ? `${confidence.toFixed(1)}%`
                      : "—"}
                  </span>

                  <span
                    className={`landmark-item-status ${
                      corrected ? "corrected" : ""
                    }`}
                  >
                    {corrected ? "Edited" : "AI"}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
};

export default LandmarkList;
