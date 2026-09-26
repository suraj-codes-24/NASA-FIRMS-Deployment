import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { MapContainer, TileLayer, CircleMarker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { fetchHotspots } from '../../api';

const regions = {
  global: { center: [20.0, 0.0], zoom: 2, bbox: null },
  north_america: { center: [45.0, -100.0], zoom: 3, bbox: "-170.0,15.0,-50.0,75.0" },
  europe: { center: [50.0, 15.0], zoom: 4, bbox: "-10.0,30.0,60.0,70.0" },
  asia: { center: [20.0, 100.0], zoom: 3, bbox: "60.0,-10.0,150.0,50.0" },
  south_america: { center: [-15.0, -60.0], zoom: 3, bbox: "-90.0,-60.0,-30.0,15.0" },
  africa: { center: [0.0, 20.0], zoom: 3, bbox: "-20.0,-35.0,55.0,38.0" }
};

const MapUpdater = ({ region }) => {
  const map = useMap();
  useEffect(() => {
    if (region && regions[region]) {
      const { center, zoom } = regions[region];
      map.flyTo(center, zoom, { duration: 1.5 });
    }
  }, [region, map]);
  return null;
};

const HeatMap = ({ filters }) => {
  const [position] = useState([22.0, 79.0]); // Center of India
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const activeFilters = {};
        if (filters?.date_from) activeFilters.date_from = filters.date_from;
        if (filters?.date_to) activeFilters.date_to = filters.date_to;
        if (filters?.ml_label) activeFilters.ml_label = filters.ml_label;
        if (filters?.min_confidence > 0) activeFilters.confidence_min = (filters.min_confidence / 100); // Hotspots API uses 0-1 or 0-100? Assuming 0-100 based on the slider which goes to 100. Actually, let's just pass it as is.
        if (filters?.min_confidence > 0) activeFilters.confidence_min = filters.min_confidence;
        if (filters?.region && filters.region !== 'global' && regions[filters.region]) {
          activeFilters.bbox = regions[filters.region].bbox;
        }

        const data = await fetchHotspots(1000, activeFilters); // Fetch up to 1000 points
        setHotspots(data);
      } catch (err) {
        console.error("Heatmap failed to fetch:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [filters]);

  const getColor = (label) => {
    if (label === 'Industrial Fire' || label === 'INDUSTRIAL_FIRE') return '#ef4444';
    if (label === 'Forest Fire' || label === 'FOREST_FIRE') return '#f97316';
    if (label === 'Gas Flare' || label === 'GAS_FLARE') return '#eab308';
    if (label === 'Agricultural Burn' || label === 'AGRICULTURAL_BURN') return '#10b981';
    if (label === 'Mining/Thermal' || label === 'MINING_THERMAL') return '#3b82f6';
    return '#9ca3af';
  };

  return (
    <div className="glass-panel" style={{ flex: 1, position: 'relative', overflow: 'hidden', padding: 0 }}>
      <MapContainer 
        center={position} 
        zoom={5} 
        style={{ height: '100%', width: '100%', backgroundColor: '#0a0b10' }} 
        zoomControl={true}
        scrollWheelZoom={true}
      >
        <MapUpdater region={filters?.region} />
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
          attribution="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ"
        />
        {/* Reference Labels (Places, Borders) for Dark Map */}
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}"
        />
        
        {/* Simulate heatmap effect with blurred circles */}
        {hotspots.map((pt, i) => {
          const color = getColor(pt.ml_label);
          // Scale intensity slightly based on FRP if available, else default to 20
          const frp = pt.frp || 15;
          const intensity = Math.min(Math.max(frp / 8, 8), 35);
          
          return (
            <React.Fragment key={i}>
              {/* Inner Core Glow */}
              <CircleMarker
                center={[pt.latitude, pt.longitude]}
                radius={intensity}
                pathOptions={{
                  color: 'transparent',
                  fillColor: color,
                  fillOpacity: 0.4,
                }}
              />
              {/* Outer Dispersion Glow */}
              <CircleMarker
                center={[pt.latitude, pt.longitude]}
                radius={intensity * 2.5}
                pathOptions={{
                  color: 'transparent',
                  fillColor: color,
                  fillOpacity: 0.1,
                }}
              />
              {/* Hotspot Pin */}
              <CircleMarker
                center={[pt.latitude, pt.longitude]}
                radius={3}
                pathOptions={{
                  color: '#fff',
                  weight: 1,
                  fillColor: color,
                  fillOpacity: 1,
                }}
              />
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Loading Overlay */}
      {loading && (
        <div style={{ position: 'absolute', top: '15px', left: '50%', transform: 'translateX(-50%)', zIndex: 1000, background: 'rgba(0,0,0,0.7)', padding: '6px 14px', borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '8px', color: '#00a8ff', fontSize: '11px', fontWeight: 600, letterSpacing: '1px', border: '1px solid rgba(0, 168, 255, 0.3)' }}>
          <Loader2 size={14} className="spin" /> UPDATING MAP
        </div>
      )}

      {/* Map Overlay info */}
      <div style={{ position: 'absolute', bottom: '15px', right: '15px', zIndex: 1000, fontSize: '10px', color: 'rgba(255,255,255,0.4)', backgroundColor: 'rgba(0,0,0,0.6)', padding: '4px 8px', borderRadius: '4px' }}>
        Thermal Density Map © CARTO
      </div>
    </div>
  );
};

export default HeatMap;
