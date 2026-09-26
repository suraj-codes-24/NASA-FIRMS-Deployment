import React, { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

/**
 * Leaflet heatmap layer showing hotspot density.
 * Uses leaflet.heat plugin. Points = [lat, lng, intensity].
 */
export default function HeatmapLayer({ points = [], options = {} }) {
  const map = useMap();

  useEffect(() => {
    if (!points.length) return;

    const heatData = points.map(p => [
      p.latitude || p[0],
      p.longitude || p[1],
      p.frp ? Math.min(p.frp / 100, 1) : 0.5, // Normalize FRP as intensity
    ]);

    const heatLayer = L.heatLayer(heatData, {
      radius: 20,
      blur: 15,
      maxZoom: 12,
      max: 1.0,
      gradient: {
        0.2: '#0000ff',
        0.4: '#00ff00',
        0.6: '#ffff00',
        0.8: '#ff8800',
        1.0: '#ff0000',
      },
      ...options,
    });

    heatLayer.addTo(map);
    return () => map.removeLayer(heatLayer);
  }, [map, points, options]);

  return null;
}
