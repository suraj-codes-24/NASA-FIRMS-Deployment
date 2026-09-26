import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

import { API_BASE } from '../config';

/**
 * Custom hook for fetching and managing hotspot data from the API.
 * Supports filtering by date range, classification type, confidence, and bbox.
 */
export default function useHotspots(filters = {}) {
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHotspots = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (filters.classification) params.classification = filters.classification;
      if (filters.minConfidence) params.min_confidence = filters.minConfidence;
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
      if (filters.limit) params.limit = filters.limit;

      const res = await axios.get(`${API_BASE}/hotspots`, { params });
      setHotspots(res.data || []);
    } catch (err) {
      console.error('Error fetching hotspots:', err);
      setError(err.message);
      setHotspots([]);
    } finally {
      setLoading(false);
    }
  }, [
    filters.classification, filters.minConfidence,
    filters.startDate, filters.endDate, filters.limit,
  ]);

  useEffect(() => {
    fetchHotspots();
  }, [fetchHotspots]);

  return { hotspots, loading, error, refetch: fetchHotspots };
}
