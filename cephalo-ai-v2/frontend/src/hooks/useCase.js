
import { useCallback, useState } from "react";

import {
  uploadCase as uploadCaseAPI,
  runInference as runInferenceAPI,
  getCase as getCaseAPI,
  updateLandmark as updateLandmarkAPI,
  resetCase as resetCaseAPI,
  getFileUrl,
} from "../services/api";

const normalizeCase = (data) => ({
  ...data,
  caseId: data.case_id,
  imageUrl: getFileUrl(data.image_url),
  imageWidth: data.image_width ?? data.width,
  imageHeight: data.image_height ?? data.height,
  points: data.points ?? [],
  measurements: data.measurements ?? {},
  clinicalAnalysis: data.clinical_analysis ?? null,
  heatmapOverlayUrl: data.heatmap_overlay_url
    ? getFileUrl(data.heatmap_overlay_url)
    : null,
});

export default function useCase() {
  const [caseData, setCaseData] = useState(null);
  const [inferenceData, setInferenceData] = useState(null);

  const [landmarks, setLandmarks] = useState([]);
  const [heatmaps, setHeatmaps] = useState([]);
  const [heatmapOverlayUrl, setHeatmapOverlayUrl] = useState(null);

  const [isUploading, setIsUploading] = useState(false);
  const [isRunningInference, setIsRunningInference] = useState(false);
  const [isUpdatingLandmark, setIsUpdatingLandmark] = useState(false);

  const [error, setError] = useState(null);

  // Upload X-ray and create a new case
  const upload = useCallback(async (file, patientCode) => {
    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadCaseAPI(file, patientCode);
      const normalized = normalizeCase(response);

      setCaseData(normalized);
      setLandmarks(normalized.points);
      setInferenceData(null);
      setHeatmaps([]);
      setHeatmapOverlayUrl(null);

      return normalized;
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Failed to upload X-ray.";

      setError(message);
      throw err;
    } finally {
      setIsUploading(false);
    }
  }, []);

  // Run AI landmark detection
  const runDetection = useCallback(async () => {
    if (!caseData?.caseId) {
      setError("Upload an X-ray before running detection.");
      return;
    }

    setIsRunningInference(true);
    setError(null);

    try {
      const response = await runInferenceAPI(caseData.caseId);

      const overlayUrl = response.heatmap_overlay_url
        ? getFileUrl(response.heatmap_overlay_url)
        : null;

      setInferenceData(response);
      setLandmarks(response.points ?? []);
      setHeatmaps(response.heatmaps ?? []);
      setHeatmapOverlayUrl(overlayUrl);

      setCaseData((previous) => ({
        ...previous,
        points: response.points ?? [],
        measurements: response.measurements ?? {},
        clinicalAnalysis: response.clinical_analysis ?? null,
        heatmapOverlayUrl: overlayUrl,
        status: response.status,
      }));

      return response;
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "AI inference failed.";

      setError(message);
      throw err;
    } finally {
      setIsRunningInference(false);
    }
  }, [caseData?.caseId]);

  // Fetch an existing case
  const loadCase = useCallback(async (caseId) => {
    setError(null);

    try {
      const response = await getCaseAPI(caseId);
      const normalized = normalizeCase(response);

      setCaseData(normalized);
      setLandmarks(normalized.points);
      setInferenceData(null);
      setHeatmaps([]);
      setHeatmapOverlayUrl(normalized.heatmapOverlayUrl);

      return normalized;
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Failed to load case.";

      setError(message);
      throw err;
    }
  }, []);

  // Update a landmark after manual correction
  const updateLandmark = useCallback(
    async (index, x, y) => {
      if (!caseData?.caseId) return;

      setIsUpdatingLandmark(true);
      setError(null);

      try {
        const response = await updateLandmarkAPI(
          caseData.caseId,
          index,
          x,
          y
        );

        if (response.points) {
          setLandmarks(response.points);
        }

        setCaseData((previous) => ({
          ...previous,
          points: response.points ?? previous.points,
          measurements:
            response.measurements ?? previous.measurements,
          clinicalAnalysis:
            response.clinical_analysis ?? null,
        }));

        return response;
      } catch (err) {
        const message =
          err.response?.data?.detail ||
          err.message ||
          "Failed to update landmark.";

        setError(message);
        throw err;
      } finally {
        setIsUpdatingLandmark(false);
      }
    },
    [caseData?.caseId]
  );

  // Reset landmarks to original AI predictions
  const resetLandmarks = useCallback(async () => {
    if (!caseData?.caseId) return;

    setError(null);

    try {
      const response = await resetCaseAPI(caseData.caseId);

      if (response.points) {
        setLandmarks(response.points);

        setCaseData((previous) => ({
          ...previous,
          points: response.points,
          measurements:
            response.measurements ?? previous.measurements,
          clinicalAnalysis:
            response.clinical_analysis ?? null,
        }));
      } else {
        await loadCase(caseData.caseId);
      }

      return response;
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Failed to reset landmarks.";

      setError(message);
      throw err;
    }
  }, [caseData?.caseId, loadCase]);

  // Clear the current workspace
  const clearCase = useCallback(() => {
    setCaseData(null);
    setInferenceData(null);
    setLandmarks([]);
    setHeatmaps([]);
    setHeatmapOverlayUrl(null);
    setError(null);
  }, []);

  return {
    caseData,
    inferenceData,
    landmarks,
    heatmaps,
    heatmapOverlayUrl,

    isUploading,
    isRunningInference,
    isUpdatingLandmark,

    error,

    upload,
    runDetection,
    loadCase,
    updateLandmark,
    resetLandmarks,
    clearCase,
  };
}
