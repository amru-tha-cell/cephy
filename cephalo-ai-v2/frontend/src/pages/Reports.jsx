
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  FileText,
  Download,
  Printer,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

import api, { getFileUrl } from "../services/api";

const Reports = ({ caseController }) => {
  const navigate = useNavigate();

  const { caseData, landmarks = [] } = caseController;

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadReport = async () => {
    if (!caseData?.caseId) {
      setReport(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.get(
        `/api/cases/${caseData.caseId}/report`
      );

      setReport(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Unable to load the case report."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
  }, [caseData?.caseId]);

  const downloadPDF = () => {
    window.print();
  };

  if (!caseData) {
    return (
      <div className="report-page">
        <button onClick={() => navigate("/")}>
          <ArrowLeft size={18} /> Dashboard
        </button>

        <div className="report-empty">
          <FileText size={36} />
          <h2>No active case</h2>
          <p>
            Upload an X-ray and run inference before generating a report.
          </p>
          <button onClick={() => navigate("/")}>
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const measurements =
    report?.measurements ?? caseData.measurements ?? {};

  const clinical = caseData.clinicalAnalysis;

  const classification =
    clinical?.skeletal_classification;

  const jawAssessment =
    clinical?.jaw_assessment;

  const surgery =
    clinical?.surgical_considerations;

  const reportLandmarks =
    report?.landmarks ?? landmarks;

  const imageUrl =
    caseData.imageUrl ||
    (report?.image_url ? getFileUrl(report.image_url) : null);

  const formatCoordinate = (value) =>
    Number.isFinite(Number(value))
      ? Number(value).toFixed(2)
      : "—";

  return (
    <div className="report-page">
      <header className="report-header no-print">
        <button
          className="report-back-button"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

        <div className="report-header-content">
          <div>
            <span className="report-eyebrow">
              CEPHALO AI · DOCUMENTATION
            </span>
            <h1>Clinical Analysis Report</h1>
            <p>
              Structured cephalometric analysis and AI decision-support
              results.
            </p>
          </div>

          <div className="report-actions">
            <button
              onClick={loadReport}
              disabled={loading}
              className="report-secondary-button"
            >
              <RefreshCw size={16} />
              Refresh
            </button>

            <button
              onClick={downloadPDF}
              className="report-primary-button"
            >
              <Download size={17} />
              Export PDF
            </button>
          </div>
        </div>
      </header>

      {loading && (
        <div className="report-message no-print">
          Loading report data...
        </div>
      )}

      {error && (
        <div className="report-error no-print">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}

      <main className="report-document">

        {/* Report title */}
        <div className="report-document-heading">
          <div className="report-logo">
            <FileText size={25} />
            <span>CEPHALO AI</span>
          </div>

          <div>
            <h2>Cephalometric Analysis Report</h2>
            <p>AI-assisted research decision-support report</p>
          </div>
        </div>

        {/* Patient and case details */}
        <section className="report-section">
          <h3>1. Patient and Case Information</h3>

          <div className="report-info-grid">
            <div>
              <span>Patient Code</span>
              <strong>
                {report?.patient_code ||
                  caseData.patient_code ||
                  "Not specified"}
              </strong>
            </div>

            <div>
              <span>Case ID</span>
              <strong>{caseData.caseId}</strong>
            </div>

            <div>
              <span>Report Date</span>
              <strong>
                {report?.created_at
                  ? new Date(report.created_at).toLocaleDateString()
                  : new Date().toLocaleDateString()}
              </strong>
            </div>

            <div>
              <span>Analysis Status</span>
              <strong>
                {clinical?.status || "Not available"}
              </strong>
            </div>
          </div>
        </section>

        {/* X-ray */}
        <section className="report-section">
          <h3>2. X-ray Visualization</h3>

          {imageUrl ? (
            <img
              src={imageUrl}
              alt="Uploaded lateral cephalometric X-ray"
              className="report-xray-image"
            />
          ) : (
            <p>Original X-ray image is unavailable.</p>
          )}

          <p className="report-image-caption">
            Original uploaded lateral cephalometric radiograph.
          </p>
        </section>

        {/* Measurements */}
        <section className="report-section">
          <h3>3. Cephalometric Measurements</h3>

          <table className="report-table">
            <thead>
              <tr>
                <th>Measurement</th>
                <th>Value</th>
                <th>Interpretation</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>SNA</td>
                <td>{measurements.SNA ?? "—"}°</td>
                <td>Maxillary position relative to cranial base</td>
              </tr>

              <tr>
                <td>SNB</td>
                <td>{measurements.SNB ?? "—"}°</td>
                <td>Mandibular position relative to cranial base</td>
              </tr>

              <tr>
                <td>ANB</td>
                <td>{measurements.ANB ?? "—"}°</td>
                <td>Relative maxillomandibular relationship</td>
              </tr>
            </tbody>
          </table>

          {measurements.note && (
            <p className="report-note">{measurements.note}</p>
          )}
        </section>

        {/* Classification */}
        <section className="report-section">
          <h3>4. Skeletal Classification</h3>

          <div className="report-highlight">
            <span>Preliminary classification</span>
            <strong>
              {classification?.classification || "Unavailable"}
            </strong>
            <p>
              {classification?.interpretation ||
                "Classification interpretation unavailable."}
            </p>
          </div>
        </section>

        {/* Jaw assessment */}
        <section className="report-section">
          <h3>5. Jaw Assessment</h3>

          <div className="report-info-grid">
            <div>
              <span>Maxillary Assessment</span>
              <strong>
                {jawAssessment?.maxillary_assessment?.assessment ||
                  "Unavailable"}
              </strong>
              <p>
                {jawAssessment?.maxillary_assessment?.interpretation}
              </p>
            </div>

            <div>
              <span>Mandibular Assessment</span>
              <strong>
                {jawAssessment?.mandibular_assessment?.assessment ||
                  "Unavailable"}
              </strong>
              <p>
                {jawAssessment?.mandibular_assessment?.interpretation}
              </p>
            </div>
          </div>
        </section>

        {/* Surgical considerations */}
        <section className="report-section">
          <h3>6. Preliminary Surgical Considerations</h3>

          {surgery?.considerations?.length > 0 ? (
            <table className="report-table">
              <thead>
                <tr>
                  <th>Possible Evaluation</th>
                  <th>Region</th>
                  <th>Reason</th>
                </tr>
              </thead>

              <tbody>
                {surgery.considerations.map((item, index) => (
                  <tr key={index}>
                    <td>{item.procedure}</td>
                    <td>{item.region}</td>
                    <td>{item.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>
              {surgery?.summary ||
                "No surgical considerations are available."}
            </p>
          )}

          {surgery?.clinical_note && (
            <p className="report-note">{surgery.clinical_note}</p>
          )}
        </section>

        {/* Landmarks */}
        <section className="report-section">
          <h3>7. Anatomical Landmark Results</h3>

          <table className="report-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Landmark</th>
                <th>X</th>
                <th>Y</th>
                <th>Uncertainty</th>
                <th>Confidence</th>
                <th>Reliability</th>
              </tr>
            </thead>

            <tbody>
              {reportLandmarks.map((point, index) => (
                <tr key={point.index ?? index}>
                  <td>{point.index ?? index}</td>
                  <td>{point.name || "Unknown"}</td>
                  <td>{formatCoordinate(point.x)}</td>
                  <td>{formatCoordinate(point.y)}</td>
                  <td>
                    {point.uncertainty_px != null
                      ? `${formatCoordinate(point.uncertainty_px)} px`
                      : "—"}
                  </td>
                  <td>
                    {point.confidence != null
                      ? `${(point.confidence * 100).toFixed(1)}%`
                      : "—"}
                  </td>
                  <td>{point.reliability || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <p className="report-note">
            Confidence values are model-derived scores, not calibrated
            clinical probabilities.
          </p>
        </section>

        {/* Disclaimer */}
        <section className="report-disclaimer">
          <h3>8. Clinical Disclaimer</h3>

          <p>
            {clinical?.disclaimer ||
              "This report is a research decision-support output and is not a confirmed clinical diagnosis or surgical prescription."}
          </p>

          <p>
            Cephalometric measurements and preliminary surgical flags
            must be reviewed by qualified orthodontic and
            maxillofacial specialists. Treatment planning requires
            clinical examination, image calibration, dental and
            occlusal assessment, and specialist judgment.
          </p>
        </section>

        <footer className="report-footer">
          <span>Cephalo AI · Research Prototype</span>
          <span>Case #{caseData.caseId}</span>
        </footer>
      </main>

      <div className="report-print-hint no-print">
        <Printer size={16} />
        Select Export PDF to open the print dialog, then choose
        "Save as PDF".
      </div>
    </div>
  );
};

export default Reports;
