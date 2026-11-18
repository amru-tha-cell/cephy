
import React from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Activity,
  Bone,
  ClipboardList,
  AlertTriangle,
  CheckCircle2,
  Info,
} from "lucide-react";

import useCase from "../hooks/useCase";

  const AnalysisWorkspace = ({ caseController }) => {
  const navigate = useNavigate();

  const {
    caseData,
    landmarks,
    inferenceData,
  } = caseController;
  const clinicalAnalysis = caseData?.clinicalAnalysis;

  const measurements = caseData?.measurements ?? {};

  const classification =
    clinicalAnalysis?.skeletal_classification;

  const jawAssessment =
    clinicalAnalysis?.jaw_assessment;

  const surgicalAssessment =
    clinicalAnalysis?.surgical_considerations;

  const considerations =
    surgicalAssessment?.considerations ?? [];

  const hasAnalysis =
    clinicalAnalysis?.status === "completed";

  const MetricCard = ({ title, value, description }) => (
    <div className="analysis-metric-card">
      <span>{title}</span>
      <strong>{value ?? "Unavailable"}</strong>
      <p>{description}</p>
    </div>
  );

  const JawCard = ({ title, assessment }) => (
    <div className="analysis-section-card">
      <h3>{title}</h3>

      <div className="analysis-highlight">
        {assessment?.assessment ?? "Unavailable"}
      </div>

      <p>
        Measurement: {assessment?.measurement ?? "N/A"}
      </p>

      <p>
        Value:{" "}
        {assessment?.value != null
          ? `${assessment.value}°`
          : "Unavailable"}
      </p>

      <p>
        {assessment?.interpretation ??
          "No interpretation available."}
      </p>

      {assessment?.reference_range && (
        <div className="analysis-reference">
          <strong>Preliminary reference range</strong>
          <p>
            {assessment.reference_range.lower}° –{" "}
            {assessment.reference_range.upper}°
          </p>
        </div>
      )}
    </div>
  );

  return (
    <div className="analysis-page">

      {/* Header */}
      <header className="analysis-page-header">
        <button
          className="analysis-back-button"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={18} />
          Back to Dashboard
        </button>

        <div>
          <span className="analysis-eyebrow">
            CEPHALO AI · CLINICAL DECISION SUPPORT
          </span>

          <h1>Cephalometric Analysis</h1>

          <p>
            Detailed interpretation of AI-generated
            cephalometric measurements and assessments.
          </p>
        </div>

        <div className="analysis-case-info">
          <span>Case ID</span>
          <strong>
            {caseData?.caseId ?? "No active case"}
          </strong>
        </div>
      </header>

      {!caseData ? (
        <div className="analysis-empty">
          <Info size={32} />
          <h2>No active case</h2>
          <p>
            Upload an X-ray and run AI detection from the
            dashboard before viewing the analysis.
          </p>

          <button onClick={() => navigate("/")}>
            Go to Dashboard
          </button>
        </div>
      ) : !hasAnalysis ? (
        <div className="analysis-empty">
          <Activity size={32} />
          <h2>Analysis not available</h2>
          <p>
            Run AI inference on the dashboard to generate
            the clinical analysis.
          </p>

          <button onClick={() => navigate("/")}>
            Return to Dashboard
          </button>
        </div>
      ) : (
        <main className="analysis-content">

          {/* Summary */}
          <section className="analysis-summary">
            <div>
              <span className="analysis-section-label">
                SKELETAL CLASSIFICATION
              </span>

              <h2>
                {classification?.classification ??
                  "Unavailable"}
              </h2>

              <p>
                {classification?.interpretation}
              </p>
            </div>

            <div className="analysis-status">
              <CheckCircle2 size={18} />
              Analysis completed
            </div>
          </section>

          {/* Measurements */}
          <section className="analysis-section">
            <div className="analysis-section-heading">
              <Activity size={21} />
              <div>
                <h2>Cephalometric Measurements</h2>
                <p>
                  Angular measurements calculated from
                  detected landmarks.
                </p>
              </div>
            </div>

            <div className="analysis-metrics-grid">
              <MetricCard
                title="SNA"
                value={
                  measurements.SNA != null
                    ? `${measurements.SNA}°`
                    : null
                }
                description="Maxillary position relative to the cranial base"
              />

              <MetricCard
                title="SNB"
                value={
                  measurements.SNB != null
                    ? `${measurements.SNB}°`
                    : null
                }
                description="Mandibular position relative to the cranial base"
              />

              <MetricCard
                title="ANB"
                value={
                  measurements.ANB != null
                    ? `${measurements.ANB}°`
                    : null
                }
                description="Relative maxillary and mandibular relationship"
              />
            </div>

            {measurements.note && (
              <div className="analysis-note">
                <Info size={18} />
                <p>{measurements.note}</p>
              </div>
            )}
          </section>

          {/* Jaw assessment */}
          <section className="analysis-section">
            <div className="analysis-section-heading">
              <Bone size={21} />
              <div>
                <h2>Jaw Assessment</h2>
                <p>
                  Preliminary interpretation of SNA and SNB.
                </p>
              </div>
            </div>

            <div className="analysis-two-column">
              <JawCard
                title="Maxillary Assessment"
                assessment={jawAssessment?.maxillary_assessment}
              />

              <JawCard
                title="Mandibular Assessment"
                assessment={jawAssessment?.mandibular_assessment}
              />
            </div>
          </section>

          {/* Surgical considerations */}
          <section className="analysis-section">
            <div className="analysis-section-heading">
              <ClipboardList size={21} />
              <div>
                <h2>Surgical Considerations</h2>
                <p>
                  Preliminary rule-based decision-support flags.
                </p>
              </div>
            </div>

            {considerations.length > 0 ? (
              <div className="analysis-surgery-list">
                {considerations.map((item, index) => (
                  <div
                    className="analysis-surgery-card"
                    key={index}
                  >
                    <div className="analysis-surgery-icon">
                      <AlertTriangle size={20} />
                    </div>

                    <div>
                      <h3>{item.procedure}</h3>
                      <p>{item.reason}</p>
                      <span>
                        Region: {item.region}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="analysis-note">
                <Info size={18} />
                <p>
                  {surgicalAssessment?.summary ??
                    "No surgical considerations available."}
                </p>
              </div>
            )}

            {surgicalAssessment?.clinical_note && (
              <div className="analysis-note">
                <Info size={18} />
                <p>{surgicalAssessment.clinical_note}</p>
              </div>
            )}
          </section>

          {/* Landmark confidence */}
          <section className="analysis-section">
            <div className="analysis-section-heading">
              <Activity size={21} />
              <div>
                <h2>Landmark Confidence Analysis</h2>
                <p>
                  Model uncertainty and reliability for the
                  detected anatomical landmarks.
                </p>
              </div>
            </div>

            <div className="analysis-table-wrapper">
              <table className="analysis-table">
                <thead>
                  <tr>
                    <th>Landmark</th>
                    <th>X</th>
                    <th>Y</th>
                    <th>Uncertainty</th>
                    <th>Confidence</th>
                    <th>Reliability</th>
                  </tr>
                </thead>

                <tbody>
                  {landmarks.map((point, index) => (
                    <tr key={point.index ?? index}>
                      <td>{point.name}</td>
                      <td>{Number(point.x).toFixed(2)}</td>
                      <td>{Number(point.y).toFixed(2)}</td>
                      <td>
                        {point.uncertainty_px != null
                          ? `${point.uncertainty_px.toFixed(2)} px`
                          : "N/A"}
                      </td>
                      <td>
                        {point.confidence != null
                          ? `${(point.confidence * 100).toFixed(1)}%`
                          : "N/A"}
                      </td>
                      <td>
                        <span
                          className={`analysis-reliability ${
                            (point.reliability || "unknown").toLowerCase()
                          }`}
                        >
                          {point.reliability ?? "Unknown"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="analysis-footnote">
              Confidence values are model-derived scores and
              should not be interpreted as calibrated clinical
              probabilities.
            </p>
          </section>

          {/* Clinical disclaimer */}
          <section className="analysis-disclaimer">
            <AlertTriangle size={22} />

            <div>
              <h3>Clinical Disclaimer</h3>

              <p>
                {clinicalAnalysis.disclaimer}
              </p>

              <p>
                This analysis is a research decision-support
                output. It is not a confirmed clinical diagnosis
                or surgical prescription. Specialist review is
                required before treatment decisions.
              </p>
            </div>
          </section>

          {/* Report navigation */}
          <div className="analysis-actions">
            <button
              onClick={() => navigate("/")}
              className="analysis-secondary-button"
            >
              Back to Dashboard
            </button>

            <button
              onClick={() => navigate("/reports")}
              className="analysis-primary-button"
            >
              View Clinical Report
            </button>
          </div>

        </main>
      )}
    </div>
  );
};

export default AnalysisWorkspace;
