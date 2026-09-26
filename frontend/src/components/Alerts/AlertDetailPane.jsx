import React, { useState, useEffect } from 'react';
import { X, MapPin, UserCheck, Activity, Clock, ShieldAlert, FileText, Crosshair } from 'lucide-react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom red flame marker for mini map
const redIcon = L.divIcon({
  className: 'custom-icon',
  html: `<div style="background-color: #ef4444; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid white; box-shadow: 0 0 15px rgba(239, 68, 68, 0.8);">
           <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>
         </div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

const AlertDetailPane = ({ selectedAlert, onAction, onClose }) => {
  const [note, setNote] = useState('');

  // Set note when a different alert is selected
  useEffect(() => {
    setNote(selectedAlert?.resolution_note || '');
  }, [selectedAlert?.id, selectedAlert?.resolution_note]);

  if (!selectedAlert) {
    return null; // Hidden when nothing is selected
  }

  const { hotspot } = selectedAlert;
  const lat = hotspot ? hotspot.latitude : 0;
  const lng = hotspot ? hotspot.longitude : 0;

  return (
    <div className="glass-panel" style={{ flex: 1, height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative', animation: 'fadeIn 0.3s ease-out' }}>
      
      {/* Top Accent Line */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '4px', background: 'linear-gradient(90deg, #00a8ff, #3b82f6)' }}></div>

      {/* Header */}
      <div style={{ padding: '20px 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-light)', backgroundColor: 'var(--bg-main)' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 600, letterSpacing: '1px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={16} color="#00a8ff" /> 
          INTELLIGENCE BRIEF: FULL REPORT
        </h3>
        <button onClick={onClose} style={{ background: 'var(--bg-hover)', border: 'none', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}>
          <X size={14} /> BACK TO DASHBOARD
        </button>
      </div>

      {/* Content */}
      <div style={{ padding: '20px 30px', flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {/* Title & Status */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--color-facility)', fontWeight: 600, letterSpacing: '1px', marginBottom: '6px' }}>INCIDENT REPORT</div>
            <h2 style={{ fontSize: '32px', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>AFD-{selectedAlert.id}</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
            <span style={{ backgroundColor: selectedAlert.status === 'RESOLVED' ? 'rgba(46, 213, 115, 0.15)' : 'rgba(255,165,2,0.15)', color: selectedAlert.status === 'RESOLVED' ? '#2ed573' : '#ffa502', border: `1px solid ${selectedAlert.status === 'RESOLVED' ? 'rgba(46, 213, 115, 0.3)' : 'rgba(255,165,2,0.3)'}`, padding: '6px 16px', borderRadius: '6px', fontSize: '12px', fontWeight: 700, letterSpacing: '0.5px' }}>{selectedAlert.status}</span>
            {selectedAlert.is_read && selectedAlert.status !== 'RESOLVED' && (
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--color-facility)', fontWeight: 600, textTransform: 'uppercase' }}>
                <UserCheck size={12} /> ACKNOWLEDGED BY ANALYST
              </span>
            )}
          </div>
        </div>

        {/* 2-Column Main Layout */}
        <div style={{ display: 'flex', gap: '20px', flex: 1, minHeight: 0 }}>
          
          {/* Left Column: Data & Actions */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* AI Analysis Box */}
            <div style={{ backgroundColor: 'color-mix(in srgb, var(--color-facility) 10%, transparent)', borderLeft: '4px solid var(--color-facility)', padding: '16px 20px', borderRadius: '0 8px 8px 0' }}>
              <h4 style={{ fontSize: '12px', color: 'var(--color-facility)', fontWeight: 600, letterSpacing: '0.5px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}><Activity size={14}/> AI ANALYSIS</h4>
              <p style={{ fontSize: '14px', margin: 0, color: 'var(--text-secondary)', lineHeight: '1.7' }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{selectedAlert.alert_type}</span> detected.
                {hotspot && ` Thermal signature exhibits FRP of `}
                {hotspot && <span style={{ color: 'var(--color-industrial)', fontWeight: 600 }}>{hotspot.frp} MW</span>}
                {hotspot && ` with a classification confidence of `}
                {hotspot && <span style={{ color: 'var(--color-agri)', fontWeight: 600 }}>{hotspot.confidence}%</span>}.
              </p>
            </div>

            {/* Metric Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div style={{ backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-light)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', fontWeight: 500, letterSpacing: '0.5px' }}><Crosshair size={14}/> COORDINATES (LAT / LONG)</div>
                <div style={{ fontSize: '16px', fontWeight: 600, fontFamily: 'monospace', color: 'var(--color-gasflare)' }}>{lat.toFixed(4)}, {lng.toFixed(4)}</div>
              </div>
              <div style={{ backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-light)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', fontWeight: 500, letterSpacing: '0.5px' }}><Clock size={14}/> TIME ACQUIRED (UTC)</div>
                <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)' }}>{hotspot ? new Date(hotspot.acq_date).toLocaleString([], {year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'}) : 'N/A'}</div>
              </div>
            </div>

            {/* Notes Area */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.5px', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}><FileText size={14}/> ANALYST NOTES / RESOLUTION</h4>
              <textarea 
                value={note}
                onChange={(e) => setNote(e.target.value)}
                disabled={selectedAlert.status === 'RESOLVED'}
                style={{ 
                  flex: 1, minHeight: '80px', resize: 'none', backgroundColor: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.08)', 
                  borderRadius: '8px', color: 'white', padding: '12px', outline: 'none', fontSize: '13px', colorScheme: 'dark', fontFamily: 'inherit',
                  transition: 'border-color 0.2s', boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)', lineHeight: '1.6'
                }} 
                placeholder="Document findings, cross-reference industrial assets, or provide resolution logic..."
                onFocus={(e) => e.target.style.borderColor = '#00a8ff'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.08)'}
              />
            </div>
            
            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '16px', marginTop: 'auto' }}>
              {selectedAlert.status !== 'RESOLVED' && (
                <button style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.2)', background: 'rgba(255, 255, 255, 0.05)', color: 'white', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '12px', letterSpacing: '0.5px' }} onClick={() => onAction('save_notes', note)}>
                  <FileText size={16} /> SAVE NOTE
                </button>
              )}
              {selectedAlert.status !== 'RESOLVED' && (
                <button style={{ flex: 1, padding: '12px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #00a8ff, #3742fa)', color: 'white', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '12px', letterSpacing: '0.5px', boxShadow: '0 4px 15px rgba(0, 168, 255, 0.3)' }} onClick={() => onAction('acknowledge', note)}>
                  <UserCheck size={16} /> ACKNOWLEDGE
                </button>
              )}
              {selectedAlert.status !== 'RESOLVED' && (
                <button style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid rgba(46, 213, 115, 0.3)', background: 'rgba(46, 213, 115, 0.1)', color: '#2ed573', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '12px', letterSpacing: '0.5px' }} onClick={() => onAction('resolve', note)}>
                  MARK RESOLVED
                </button>
              )}
            </div>

          </div>

          {/* Right Column: Large Map */}
          <div style={{ flex: 1.5, borderRadius: '12px', overflow: 'hidden', position: 'relative', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
            <MapContainer center={[lat, lng]} zoom={14} style={{ height: '100%', width: '100%', backgroundColor: '#000' }} zoomControl={true} attributionControl={false}>
              <TileLayer url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" />
              <TileLayer url="https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}&hl=en" />
              <Marker position={[lat, lng]} icon={redIcon} />
            </MapContainer>
            {/* Map Overlay Vignette */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none', boxShadow: 'inset 0 0 50px rgba(0,0,0,0.5)', zIndex: 1000 }}></div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default AlertDetailPane;
