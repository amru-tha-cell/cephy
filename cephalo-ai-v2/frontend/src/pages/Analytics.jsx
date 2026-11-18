
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Activity,
  Brain,
  Users,
  Target,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

import api from "../services/api";

const Analytics = ({ caseController }) => {
  const navigate = useNavigate();

  const {
    caseData,
    landmarks = [],
    inferenceData,
  } = caseController;

  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [summaryError, setSummaryError] = useState(null);

  const loadAnalytics = async () => {
    setLoading(true);
    setSummaryError(null);

    try {
      const response = await api.get("/api/analytics/summary");
      setSummary(response.data);
    } catch (error) {
      setSummaryError(
        error.response?.data?.detail ||
        error.message ||
        "Could not load analytics summary."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const reliability = useMemo(() => {
    return landmarks.reduce(
      (result, point) => {
        const level = (point.reliability || "Unknown").toLowerCase();

        if (level === "high") result.high += 1;
        else if (level === "moderate") result.moderate += 1;
        else if (level === "low") result.low += 1;
        else result.unknown += 1;

        return result;
      },
      { high: 0, moderate: 0, low: 0, unknown: 0 }
    );
  }, [landmarks]);

  const confidenceValues = landmarks
    .map((point) => point.confidence)
    .filter((value) => Number.isFinite(value));

  const averageConfidence =
    confidenceValues.length > 0
      ? (
          confidenceValues.reduce((sum, value) => sum + value, 0) /
          confidenceValues.length
        ) * 100
      : null;

  const averageUncertaintyValues = landmarks
    .map((point) => point.uncertainty_px)
    .filter((value) => Number.isFinite(value));

  const averageUncertainty =
    averageUncertaintyValues.length > 0
      ? averageUncertaintyValues.reduce((sum, value) => sum + value, 0) /
        averageUncertaintyValues.length
      : null;

  const measurements = caseData?.measurements ?? {};
  const clinical = caseData?.clinicalAnalysis;

  const formatValue = (value) =>
    value === null || value === undefined ? "—" : value;

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <button
          className="analytics-back-button"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

        <div className="analytics-title-row">
          <div>
            <span className="analytics-eyebrow">
              CEPHALO AI · PERFORMANCE OVERVIEW
            </span>
            <h1>Analytics Dashboard</h1>
            <p>
              Overview of model activity, case statistics and
              landmark prediction reliability.
            </p>
          </div>

          <button
            className="analytics-refresh-button"
            onClick={loadAnalytics}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </header>

      <main className="analytics-content">
        <section className="analytics-stat-grid">
          <div className="analytics-stat-card">
            <div className="analytics-stat-icon">
              <Users size={21} />
            </div>
            <span>Total Cases</span>
            <strong>
              {formatValue(
                summary?.total_cases ??
                summary?.totalCases
              )}
            </strong>
            <p>Cases recorded by the backend</p>
          </div>

          <div className="analytics-stat-card">
            <div className="analytics-stat-icon">
              <Brain size={21} />
            </div>
            <span>Current Case Landmarks</span>
            <strong>{landmarks.length} / 19</strong>
            <p>Detected landmarks in the active case</p>
          </div>

          <div className="analytics-stat-card">
            <div className="analytics-stat-icon">
              <Target size={21} />
            </div>
            <span>Average Confidence</span>
            <strong>
              {averageConfidence !== null
                ? `${averageConfidence.toFixed(1)}%`
                : "—"}
            </strong>
            <p>Mean model confidence score</p>
          </div>

          <div className="analytics-stat-card">
            <div className="analytics-stat-icon">
              <Activity size={21} />
            </div>
            <span>Average Uncertainty</span>
            <strong>
              {averageUncertainty !== null
                ? `${averageUncertainty.toFixed(2)} px`
                : "—"}
            </strong>
            <p>Mean landmark coordinate uncertainty</p>
          </div>
        </section>

        <section className="analytics-panel">
          <div className="analytics-panel-heading">
            <div>
              <h2>Active Case Overview</h2>
              <p>Measurements from the currently selected case.</p>
            </div>
            <span className="analytics-case-badge">
              {caseData ? `Case #${caseData.caseId}` : "No active case"}
            </span>
          </div>

          {!caseData ? (
            <p className="analytics-empty">
              Upload an X-ray from the Dashboard to view case analytics.
            </p>
          ) : (
            <>
              <div className="analytics-measurements">
                {["SNA", "SNB", "ANB"].map((key) => (
                  <div className="analytics-measurement" key={key}>
                    <span>{key}</span>
                    <strong>
                      {measurements[key] != null
                        ? `${measurements[key]}°`
                        : "Unavailable"}
                    </strong>
                  </div>
                ))}
              </div>

              <div className="analytics-case-details">
                <p>
                  <strong>Patient code:</strong>{" "}
                  {caseData.patient_code || "Not specified"}
                </p>
                <p>
                  <strong>Classification:</strong>{" "}
                  {clinical?.skeletal_classification?.classification ||
                    "Not available"}
                </p>
                <p>
                  <strong>Analysis status:</strong>{" "}
                  {clinical?.status || "Not generated"}
                </p>
                <p>
                  <strong>Inference samples:</strong>{" "}
                  {inferenceData?.mc_samples ?? "Unavailable"}
                </p>
              </div>
            </>
          )}
        </section>

        <section className="analytics-panel">
          <div className="analytics-panel-heading">
            <div>
              <h2>Landmark Reliability</h2>
              <p>
                Distribution of model reliability levels for the active
                case.
              </p>
            </div>
          </div>

          {landmarks.length === 0 ? (
            <p className="analytics-empty">
              Run inference to view landmark reliability statistics.
            </p>
          ) : (
            <>
              <div className="analytics-reliability-grid">
                <div className="reliability-card high">
                  <span>High</span>
                  <strong>{reliability.high}</strong>
                </div>

                <div className="reliability-card moderate">
                  <span>Moderate</span>
                  <strong>{reliability.moderate}</strong>
                </div>

                <div className="reliability-card low">
                  <span>Low</span>
                  <strong>{reliability.low}</strong>
                </div>

                <div className="reliability-card unknown">
                  <span>Unknown</span>
                  <strong>{reliability.unknown}</strong>
                </div>
              </div>

              <div className="analytics-reliability-bar">
                {[
                  { key: "high", value: reliability.high },
                  { key: "moderate", value: reliability.moderate },
                  { key: "low", value: reliability.low },
                  { key: "unknown", value: reliability.unknown },
                ].map((item) => (
                  <div
                    key={item.key}
                    className={`reliability-segment ${item.key}`}
                    style={{
                      width: `${(item.value / landmarks.length) * 100}%`,
                    }}
                  />
                ))}
              </div>

              <p className="analytics-footnote">
                Reliability categories are based on the model's uncertainty
                thresholds. They are not clinical accuracy measurements.
              </p>
            </>
          )}
        </section>

        <section className="analytics-panel">
          <div className="analytics-panel-heading">
            <div>
              <h2>Backend Analytics Summary</h2>
              <p>Statistics returned by the analytics API.</p>
            </div>
          </div>

          {loading ? (
            <p className="analytics-empty">Loading analytics...</p>
          ) : summaryError ? (
            <div className="analytics-error">
              <AlertTriangle size={18} />
              {summaryError}
            </div>
          ) : summary ? (
            <div className="analytics-summary-grid">
              {Object.entries(summary)
                .filter(
                  ([, value]) =>
                    typeof value === "number" ||
                    typeof value === "string"
                )
                .map(([key, value]) => (
                  <div className="analytics-summary-item" key={key}>
                    <span>
                      {key.replace(/_/g, " ")}
                    </span>
                    <strong>{String(value)}</strong>
                  </div>
                ))}
            </div>
          ) : (
            <p className="analytics-empty">
              No backend summary is available.
            </p>
          )}
        </section>

        <section className="analytics-disclaimer">
          <CheckCircle2 size={20} />
          <p>
            These statistics describe model outputs and application
            activity. They do not establish clinical diagnostic accuracy
            or treatment suitability.
          </p>
        </section>

        <div className="analytics-actions">
          <button onClick={() => navigate("/")}>
            Return to Dashboard
          </button>
          <button
            className="analytics-primary-button"
            onClick={() => navigate("/analysis")}
            disabled={!caseData}
          >
            View Detailed Analysis
          </button>
        </div>
      </main>
    </div>
  );
};

export default Analytics;
