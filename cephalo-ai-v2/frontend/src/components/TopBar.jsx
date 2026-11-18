
import React, { useRef, useState } from "react";
import { Activity, Upload, ScanSearch, CircleDot } from "lucide-react";

const TopBar = ({
  caseData,
  isUploading,
  isRunningInference,
  onUpload,
  onRunDetection,
  backendOnline = null,
}) => {
  const fileInputRef = useRef(null);
  const [patientCode, setPatientCode] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      fileInputRef.current?.click();
      return;
    }

    if (!patientCode.trim()) {
      alert("Please enter a patient code.");
      return;
    }

    try {
      await onUpload?.(selectedFile, patientCode.trim());

      setSelectedFile(null);
      setPatientCode("");

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  const backendStatus =
    backendOnline === true
      ? "Connected"
      : backendOnline === false
        ? "Disconnected"
        : "Checking";

  return (
    <header className="topbar">
      <div className="topbar-brand">
        <div className="brand-icon">
          <Activity size={21} />
        </div>

        <div>
          <h1>Cephalo<span>AI</span></h1>
          <p>LANDMARK DETECTION SYSTEM</p>
        </div>
      </div>

      <div className="topbar-center">
        <div className="backend-status">
          <CircleDot
            size={9}
            className={
              backendOnline === true
                ? "status-online"
                : backendOnline === false
                  ? "status-offline"
                  : "status-checking"
            }
          />

          <span>{backendStatus}</span>
        </div>

        <div className="case-indicator">
          <span>ACTIVE CASE</span>
          <strong>
            {caseData?.caseId
              ? `#${caseData.caseId}`
              : "No case loaded"}
          </strong>
        </div>
      </div>

      <div className="topbar-actions">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          hidden
        />

        <input
          type="text"
          className="patient-code-input"
          placeholder="Patient code"
          value={patientCode}
          onChange={(event) =>
            setPatientCode(event.target.value)
          }
        />

        <button
          type="button"
          className="topbar-button upload-button"
          onClick={handleUpload}
          disabled={isUploading}
        >
          <Upload size={15} />

          {isUploading
            ? "Uploading..."
            : selectedFile
              ? "Upload X-ray"
              : "Choose X-ray"}
        </button>

        <button
          type="button"
          className="topbar-button detect-button"
          onClick={onRunDetection}
          disabled={!caseData?.caseId || isRunningInference}
        >
          <ScanSearch size={15} />

          {isRunningInference
            ? "Detecting..."
            : "Run Detection"}
        </button>
      </div>
    </header>
  );
};

export default TopBar;
