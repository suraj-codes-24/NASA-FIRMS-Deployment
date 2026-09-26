import React from 'react';

const LEGEND_ITEMS = [
  { label: 'Industrial Fire', color: '#ef4444' },
  { label: 'Forest / Wildfire', color: '#f97316' },
  { label: 'Gas Flare', color: '#eab308' },
  { label: 'Agricultural Burn', color: '#10b981' },
  { label: 'Mining / Thermal', color: '#3b82f6' },
  { label: 'Unclassified', color: '#9ca3af' },
  { label: 'Industrial Facility', color: '#3b82f6', shape: 'square' },
];

/**
 * Map legend showing the 6-class fire taxonomy color codes
 * and the industrial facility marker.
 */
export default function MapLegend() {
  return (
    <div style={{
      position: 'absolute', bottom: 24, right: 24, zIndex: 1000,
      background: 'rgba(15, 17, 23, 0.88)', backdropFilter: 'blur(12px)',
      borderRadius: 12, padding: '14px 18px', border: '1px solid rgba(255,255,255,0.08)',
      minWidth: 180,
    }}>
      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 }}>
        Classification Legend
      </div>
      {LEGEND_ITEMS.map(item => (
        <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <span style={{
            width: 12, height: 12,
            borderRadius: item.shape === 'square' ? 2 : '50%',
            background: item.color,
            display: 'inline-block', flexShrink: 0,
            border: '1px solid rgba(255,255,255,0.15)',
          }} />
          <span style={{ fontSize: '0.8rem', color: '#d1d5db' }}>{item.label}</span>
        </div>
      ))}
    </div>
  );
}
