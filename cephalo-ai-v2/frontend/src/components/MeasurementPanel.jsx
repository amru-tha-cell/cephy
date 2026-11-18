
import React from "react";

const MEASUREMENT_INFO = {
  SNA: {
    title: "SNA",
    description: "Maxillary position",
  },
  SNB: {
    title: "SNB",
    description: "Mandibular position",
  },
  ANB: {
    title: "ANB",
    description: "Maxillomandibular relationship",
  },
};

const MeasurementPanel = ({ measurements = {} }) => {
  const getValue = (key) => {
    const value = measurements[key];

    if (value === null || value === undefined) {
      return null;
    }

    // Support either a numeric value or an object
    // containing a value field.
    const numericValue =
      typeof value === "object"
        ? value.value
        : value;

    const number = Number(numericValue);

    return Number.isFinite(number) ? number : null;
  };

  const availableMeasurements = Object.keys(MEASUREMENT_INFO);

  const hasMeasurements = availableMeasurements.some(
    (key) => getValue(key) !== null
  );

  return (
    <section className="measurement-panel">
      <div className="measurement-heading">
        <div>
          <h2>Cephalometric Measurements</h2>
          <p>Computed from predicted landmark coordinates</p>
        </div>

        <span className="measurement-unit">DEGREES</span>
      </div>

      {!hasMeasurements ? (
        <div className="measurement-empty">
          <span>—</span>
          <p>Measurements are not available yet.</p>
        </div>
      ) : (
        <div className="measurement-grid">
          {availableMeasurements.map((key) => {
            const info = MEASUREMENT_INFO[key];
            const value = getValue(key);

            return (
              <div className="measurement-card" key={key}>
                <div className="measurement-card-top">
                  <span className="measurement-name">
                    {info.title}
                  </span>

                  <span className="measurement-indicator">
                    {value !== null ? "●" : "○"}
                  </span>
                </div>

                <strong className="measurement-value">
                  {value !== null
                    ? `${value.toFixed(2)}°`
                    : "—"}
                </strong>

                <span className="measurement-description">
                  {info.description}
                </span>
              </div>
            );
          })}
        </div>
      )}

      <div className="measurement-disclaimer">
        Research prototype measurements based on predicted
        landmark coordinates. Clinical interpretation requires
        verified landmarks and appropriate calibration.
      </div>
    </section>
  );
};

export default MeasurementPanel;
