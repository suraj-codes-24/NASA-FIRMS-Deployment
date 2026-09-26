import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Flame, Clock, Shield, Factory, Sun, Navigation } from 'lucide-react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import { API_BASE } from '../config';

// Fix leafet marker icon issue
const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const classColors = {
  'Industrial Fire': '#ef4444',
  'Forest Fire': '#f97316',
  'Gas Flare': '#eab308',
  'Agricultural Burn': '#22c55e',
  'Mining/Thermal': '#3b82f6',
  'Unclassified': '#6b7280',
};

export default function HotspotDetailPage() {
  const { id } = useParams();
  const [hotspot, setHotspot] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/hotspots/${id}`)
      .then(res => setHotspot(res.data))
      .catch(() => setHotspot(null))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
        Loading hotspot intelligence...
      </div>
    );
  }

  if (!hotspot) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <h2>Hotspot #{id} not found in active telemetry.</h2>
        <Link to="/" style={{ color: 'var(--color-facility)', textDecoration: 'none', marginTop: '1rem', display: 'inline-block' }}>← Return to Map</Link>
      </div>
    );
  }

  const label = hotspot.ml_label || 'Unclassified';
  const color = classColors[label] || '#6b7280';
  const lat = hotspot.latitude || 0;
  const lng = hotspot.longitude || 0;

  return (
    <div style={{ height: '100%', width: '100%', padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
      
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', textDecoration: 'none', width: 'fit-content' }}>
        <ArrowLeft size={18} /> Back to Surveillance
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ backgroundColor: `${color}22`, padding: '12px', borderRadius: '12px', border: `1px solid ${color}44` }}>
          <Flame size={32} color={color} />
        </div>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 700, margin: '0 0 4px 0' }}>Anomaly HD-{hotspot.id}</h1>
          <span style={{
            padding: '4px 12px', borderRadius: '12px', fontSize: '13px', fontWeight: 600,
            background: `${color}22`, color: color, border: `1px solid ${color}44`, display: 'inline-block'
          }}>
            {label} Classification
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
        
        {/* Left Col: Map */}
        <div className="glass-panel" style={{ flex: '1 1 500px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Navigation size={18} color="var(--text-secondary)" />
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>Satellite Coordinates</h3>
          </div>
          <div style={{ height: '400px', width: '100%', position: 'relative' }}>
            <MapContainer center={[lat, lng]} zoom={14} style={{ height: '100%', width: '100%' }} zoomControl={false} attributionControl={false}>
              <TileLayer url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" />
              <TileLayer url="https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}&hl=en" />
              <Marker position={[lat, lng]} icon={redIcon} />
            </MapContainer>
            
            {/* Overlay Coordinates */}
            <div className="glass-panel" style={{ position: 'absolute', bottom: '16px', left: '16px', zIndex: 1000, padding: '12px 16px', display: 'flex', gap: '16px', backgroundColor: 'rgba(15, 23, 42, 0.85)' }}>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>LATITUDE</div>
                <div style={{ fontSize: '14px', fontWeight: 600, fontFamily: 'monospace' }}>{lat.toFixed(6)}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>LONGITUDE</div>
                <div style={{ fontSize: '14px', fontWeight: 600, fontFamily: 'monospace' }}>{lng.toFixed(6)}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Col: Details */}
        <div className="glass-panel" style={{ flex: '1 1 400px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0, paddingBottom: '12px', borderBottom: '1px solid var(--border-color)' }}>
            Telemetry Data
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
            <DetailItem icon={<Flame size={16} />} label="FRP (Radiative Power)" value={`${hotspot.frp?.toFixed(2)} MW`} />
            <DetailItem icon={<Sun size={16} />} label="Brightness Temp" value={`${hotspot.brightness?.toFixed(1)} K`} />
            <DetailItem icon={<Shield size={16} />} label="Sensor Confidence" value={`${hotspot.confidence?.toFixed(0)}%`} />
            <DetailItem icon={<Factory size={16} />} label="Distance to Industry" value={hotspot.dist_to_industry_m != null ? `${hotspot.dist_to_industry_m.toFixed(0)} meters` : 'Unknown'} />
          </div>

          <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0, paddingTop: '12px', paddingBottom: '12px', borderBottom: '1px solid var(--border-color)', borderTop: '1px solid var(--border-color)' }}>
            Acquisition Metadata
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
            <DetailItem icon={<Clock size={16} />} label="Acquired Timestamp" value={hotspot.acq_date ? new Date(hotspot.acq_date).toLocaleString() : '—'} />
            <DetailItem icon={<Clock size={16} />} label="Temporal Persistence" value={`${hotspot.persistence_hours?.toFixed(1) || 0} hrs`} />
            <DetailItem label="Satellite Platform" value={hotspot.satellite || '—'} />
            <DetailItem label="Instrument" value={hotspot.instrument || '—'} />
            <DetailItem label="Orbital Pass" value={hotspot.daynight === 'D' ? '☀ Day' : '🌙 Night'} />
            <DetailItem label="ML Model Confidence" value={`${hotspot.classification_confidence?.toFixed(1) || 0}%`} />
          </div>

        </div>

      </div>
    </div>
  );
}

function DetailItem({ icon, label, value }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <span style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6 }}>
        {icon} {label}
      </span>
      <span style={{ fontSize: '15px', fontWeight: 500 }}>{value ?? '—'}</span>
    </div>
  );
}
