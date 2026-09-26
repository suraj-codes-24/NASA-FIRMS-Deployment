/**
 * IGNIS — API Service
 * 
 * Axios HTTP client for backend API communication.
 * Base URL configured via VITE_API_URL environment variable.
 */

import axios from 'axios'

import { API_BASE } from '../config';
const API_BASE_URL = API_BASE;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor — attach JWT token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ignis_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ignis_token')
      // Optionally redirect to login
    }
    return Promise.reject(error)
  }
)

export default api

// ----- API Functions (will be populated as endpoints are built) -----

export const hotspotAPI = {
  getAll: (params) => api.get('/hotspots', { params }),
  getById: (id) => api.get(`/hotspots/${id}`),
  getLatest: (limit = 100) => api.get('/hotspots/latest', { params: { limit } }),
  getHeatmap: (params) => api.get('/hotspots/heatmap', { params }),
  getHistory: (id, days = 30) => api.get(`/hotspots/${id}/history`, { params: { days } }),
}

export const facilityAPI = {
  getAll: (params) => api.get('/facilities', { params }),
  getById: (id) => api.get(`/facilities/${id}`),
  getHotspots: (id, params) => api.get(`/facilities/${id}/hotspots`, { params }),
}

export const analyticsAPI = {
  getSummary: (params) => api.get('/analytics/summary', { params }),
  getTimeline: (params) => api.get('/analytics/timeline', { params }),
  getClassification: (params) => api.get('/analytics/classification', { params }),
  getTopStates: (params) => api.get('/analytics/top-states', { params }),
  getPersistence: (params) => api.get('/analytics/persistence', { params }),
}

export const alertAPI = {
  getAll: (params) => api.get('/alerts', { params }),
  getById: (id) => api.get(`/alerts/${id}`),
  acknowledge: (id) => api.put(`/alerts/${id}/acknowledge`),
  resolve: (id, note) => api.put(`/alerts/${id}/resolve`, { resolution_note: note }),
}

export const reportAPI = {
  generate: (body) => api.post('/reports/generate', body),
  download: (id) => api.get(`/reports/${id}/download`, { responseType: 'blob' }),
}

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
}
