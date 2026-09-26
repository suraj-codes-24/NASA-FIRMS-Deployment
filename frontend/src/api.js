import { API_BASE } from './config';
import axios from 'axios';

// Create an axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchHotspots = async (limit = 1000, filters = {}) => {
  try {
    const response = await api.get(`/hotspots`, { params: { limit, ...filters } });
    return response.data;
  } catch (error) {
    console.error('Error fetching hotspots:', error);
    return [];
  }
};

export const fetchFacilities = async (limit = 100) => {
  try {
    const response = await api.get(`/facilities`, { params: { limit } });
    return response.data;
  } catch (error) {
    console.error('Error fetching facilities:', error);
    return [];
  }
};

// --- Analytics ---
export const fetchAnalyticsSummary = async (filters = {}) => {
  const response = await api.get(`/analytics/summary`, { params: filters });
  return response.data;
};

export const fetchAnalyticsClassification = async (filters = {}) => {
  const response = await api.get(`/analytics/classification`, { params: filters });
  return response.data;
};

export const fetchAnalyticsTimeline = async (filters = {}) => {
  const response = await api.get(`/analytics/timeline`, { params: filters });
  return response.data;
};

// --- Settings ---
export const fetchSettings = async () => {
  const response = await api.get(`/settings`);
  return response.data;
};

export const updateSettings = async (settings) => {
  const response = await api.post(`/settings`, { settings });
  return response.data;
};

// --- Auth ---
export const changePassword = async (newPassword) => {
  const response = await api.post(`/auth/change-password`, { new_password: newPassword });
  return response.data;
};

export const logout = async () => {
  const response = await api.post(`/auth/logout`);
  return response.data;
};

// --- Alerts ---
export const fetchAlerts = async () => {
  const response = await api.get(`/alerts`);
  return response.data;
};

export const acknowledgeAlert = async (id) => {
  const response = await api.put(`/alerts/${id}/acknowledge`);
  return response.data;
};

export const resolveAlert = async (id, resolution_note) => {
  const response = await api.put(`/alerts/${id}/resolve`, { resolution_note });
  return response.data;
};

export const saveAlertNotes = async (id, resolution_note) => {
  const response = await api.put(`/alerts/${id}/notes`, { resolution_note });
  return response.data;
};

// --- Reports & Auth ---
export const login = async (username, password) => {
  const response = await api.post(`/auth/login`, { username, password });
  return response.data;
};

export const fetchCurrentUser = async () => {
  const response = await api.get(`/auth/me`);
  return response.data;
};

export const fetchReportSummary = async () => {
  const response = await api.get(`/reports/summary`);
  return response.data;
};

export const generateReport = async (filters = {}) => {
  // Use axios.post to get the blob directly using our configured api instance
  const response = await api.post(`/reports/generate`, null, {
    params: filters,
    responseType: 'blob'
  });
  return response.data;
};

export default api;
