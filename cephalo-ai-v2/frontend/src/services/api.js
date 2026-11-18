
import axios from "axios";

export const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

// Upload an X-ray and create a case
export const uploadCase = async (file, patientCode) => {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("patient_code", patientCode);

  const response = await api.post("/api/cases", formData);

  return response.data;
};

// Run AI landmark detection
export const runInference = async (caseId) => {
  const response = await api.post(
    `/api/cases/${caseId}/inference`
  );

  return response.data;
};

// Retrieve case details
export const getCase = async (caseId) => {
  const response = await api.get(
    `/api/cases/${caseId}`
  );

  return response.data;
};

// Update a landmark after manual correction
export const updateLandmark = async (caseId, index, x, y) => {
  const response = await api.patch(
    `/api/cases/${caseId}/landmarks/${index}`,
    { x, y }
  );

  return response.data;
};

// Reset landmarks to original AI predictions
export const resetCase = async (caseId) => {
  const response = await api.post(
    `/api/cases/${caseId}/reset`
  );

  return response.data;
};

// Retrieve analytics
export const getAnalytics = async () => {
  const response = await api.get("/api/analytics/summary");

  return response.data;
};

// Retrieve case comparison
export const getComparison = async (caseId) => {
  const response = await api.get(
    `/api/cases/${caseId}/comparison`
  );

  return response.data;
};

// Retrieve case report
export const getReport = async (caseId) => {
  const response = await api.get(
    `/api/cases/${caseId}/report`
  );

  return response.data;
};

// Convert backend static file paths into usable URLs
export const getFileUrl = (path) => {
  if (!path) return "";

  return new URL(path, API_BASE_URL).toString();
};

export default api;
