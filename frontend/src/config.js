const rawBase = import.meta.env.VITE_API_BASE_URL;
const cleanBase = rawBase ? rawBase.replace(/\/$/, '') : '';

export const API_BASE = cleanBase 
  ? `${cleanBase}/api/v1`
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1');

export const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
