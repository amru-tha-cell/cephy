
import React, { useEffect, useState } from "react";

import TopBar from "../components/TopBar";
import LandmarkList from "../components/LandmarkList";
import XrayCanvas from "../components/XrayCanvas";
import LandmarkDetails from "../components/LandmarkDetails";
import MeasurementPanel from "../components/MeasurementPanel";

import api from "../services/api";

const Dashboard = ({ caseController }) => {
  const {
    caseData,
    landmarks,
    heatmaps,
    heatmapOverlayUrl,
    isUploading,
    isRunningInference,
    isUpdatingLandmark,
    error,
    upload,
    runDetection,
    updateLandmark,
    resetLandmarks,
  } = caseController;

  const [selectedIndex, setSelectedIndex] = useState(null);
  const [backendOnline, setBackendOnline] = useState(null);

  // Check whether FastAPI is reachable.
  useEffect(() => {
    let isMounted = true;

    const checkBackend = async () => {
      try {
        await api.get("/api/health");

        if (isMounted) {
          setBackendOnline(true);
        }
      } catch {
        if (isMounted) {
          setBackendOnline(false);
        }
      }
    };

    checkBackend();

    return () => {
      isMounted = false;
    };
  }, []);

  // Upload a new X-ray.
  const handleUpload = async (file, patientCode) => {
    const result = await upload(file, patientCode);
    setSelectedIndex(null);
    return result;
  };

  // Run model inference.
  const handleDetection = async () => {
    try {
      const result = await runDetection();

      if (result?.points?.length > 0) {
        setSelectedIndex(0);
      }
    } catch (err) {
      console.error("Inference failed:", err);
    }
  };

  // Save manually corrected landmark coordinates.
  const handleLandmarkUpdate = async (index, x, y) => {
    try {
      await updateLandmark(index, x, y);
    } catch (err) {
      console.error("Could not save landmark correction:", err);
      throw err;
    }
  };

  // Reset all landmarks to their original AI predictions.
  const handleReset = async () => {
    const confirmed = window.confirm(
      "Reset all landmarks to their original AI predictions?"
    );

    if (!confirmed) return;

    try {
      await resetLandmarks();
    } catch (err) {
      console.error("Could not reset landmarks:", err);
    }
  };

  const selectedPoint =
    selectedIndex !== null
      ? landmarks[selectedIndex]
      : null;

  const hasPredictions = landmarks.length > 0;

  return (
    <div className="dashboard">
      <TopBar
        caseData={caseData}
        isUploading={isUploading}
        isRunningInference={isRunningInference}
        onUpload={handleUpload}
        onRunDetection={handleDetection}
        backendOnline={backendOnline}
      />

      <main className="dashboard-content">

        {/* Page heading */}
        <div className="dashboard-heading">
          <div>
            <span className="dashboard-eyebrow">
              AI-POWERED CEPHALOMETRIC ANALYSIS
            </span>

            <h1>Dashboard</h1>

            <p>
              Upload X-rays, detect anatomical landmarks,
              and review cephalometric measurements.
            </p>
          </div>

          <div className="workspace-status">
            <span
              className={`workspace-status-dot ${
                backendOnline ? "online" : "offline"
              }`}
            />

            {backendOnline === true
              ? "Backend connected"
              : backendOnline === false
                ? "Backend unavailable"
                : "Checking backend"}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="dashboard-error">
            <strong>Something went wrong</strong>
            <span>{String(error)}</span>
          </div>
        )}

        {/* Main three-column workspace */}
        <section className="workspace-grid">

          {/* Left: landmark list */}
          <LandmarkList
            landmarks={landmarks}
            selectedIndex={selectedIndex}
            onSelect={setSelectedIndex}
          />

          {/* Center: X-ray and markers */}
          <div className="workspace-center">

            <div className="canvas-heading">
              <div>
                <h2>X-ray Visualization</h2>

                <p>
                  {caseData
                    ? `Patient: ${caseData.patient_code || "Not specified"}`
                    : "Waiting for X-ray upload"}
                </p>
              </div>

              {hasPredictions && (
                <button
                  type="button"
                  className="reset-button"
                  onClick={handleReset}
                  disabled={isUpdatingLandmark}
                >
                  Reset predictions
                </button>
              )}
            </div>

            <div className="canvas-container">
              <XrayCanvas
                imageUrl={caseData?.imageUrl}
                imageWidth={caseData?.imageWidth}
                imageHeight={caseData?.imageHeight}
                landmarks={landmarks}
                heatmaps={heatmaps}
                heatmapOverlayUrl={heatmapOverlayUrl}
                selectedIndex={selectedIndex}
                onSelect={setSelectedIndex}
                onUpdateLandmark={handleLandmarkUpdate}
              />
            </div>

            {isRunningInference && (
              <div className="inference-status">
                <span className="loading-spinner" />
                Running AI landmark detection...
                This may take several seconds.
              </div>
            )}

            {isUpdatingLandmark && (
              <div className="saving-status">
                Saving landmark correction...
              </div>
            )}

            <div className="canvas-legend">
              <span>
                <i className="legend-marker cyan" />
                AI detected
              </span>

              <span>
                <i className="legend-marker amber" />
                Manually corrected
              </span>

              <span>
                <i className="legend-marker selected-marker" />
                Selected landmark
              </span>
            </div>
          </div>

          {/* Right: landmark details and measurements */}
          <aside className="workspace-right">
            <LandmarkDetails
              point={selectedPoint}
              index={selectedIndex}
              totalLandmarks={19}
            />

            <MeasurementPanel
              measurements={caseData?.measurements ?? {}}
            />
          </aside>

        </section>

        {/* Footer */}
        <footer className="dashboard-footer">
          <span>Cephalo AI · Research Prototype</span>

          <span>
            {caseData
              ? `Case #${caseData.caseId}`
              : "No active case"}
          </span>
        </footer>

      </main>
    </div>
  );
};

export default Dashboard;
