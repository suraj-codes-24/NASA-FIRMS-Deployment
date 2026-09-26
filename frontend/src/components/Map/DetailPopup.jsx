import React from 'react';
import { Link } from 'react-router-dom';
import { Flame, MapPin, Clock, Shield, ExternalLink } from 'lucide-react';

const classColors = {
  'Industrial Fire': '#ef4444',
  'Forest Fire': '#f97316',
  'Gas Flare': '#eab308',
  'Agricultural Burn': '#10b981',
  'Mining/Thermal': '#3b82f6',
  'Unclassified': '#9ca3af',
};

/**
 * Popup content shown when a hotspot marker is clicked on the map.
 * Shows classification, key metrics, and a link to the full detail page.
 */
export default function DetailPopup({ hotspot }) {
  if (!hotspot) return null;

  const label = hotspot.ml_label || 'Unclassified';
  const color = classColors[label] || '#6b7280';

  return (
    <div style={{ minWidth: 220, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <Flame size={16} color={color} />
        <strong style={{ fontSize: '0.95rem' }}>Hotspot #{hotspot.id}</strong>
      </div>

      <div style={{
        display: 'inline-block', padding: '2px 10px', borderRadius: 12,
        fontSize: '0.75rem', fontWeight: 600,
        background: `${color}22`, color: color, border: `1px solid ${color}44`,
        marginBottom: 10,
      }}>
        {label}
      </div>

      <div style={{ fontSize: '0.8rem', lineHeight: 1.8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <MapPin size={13} /> {hotspot.latitude?.toFixed(4)}, {hotspot.longitude?.toFixed(4)}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Flame size={13} /> FRP: {hotspot.frp?.toFixed(1) || '—'} MW
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Shield size={13} /> Confidence: {hotspot.confidence?.toFixed(0) || '—'}%
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Clock size={13} /> {hotspot.satellite || '—'} · {hotspot.daynight === 'D' ? 'Day' : 'Night'}
        </div>
      </div>

      <Link
        to={`/hotspot/${hotspot.id}`}
        style={{
          display: 'flex', alignItems: 'center', gap: 4, marginTop: 10,
          color: '#60a5fa', fontSize: '0.8rem', fontWeight: 500, textDecoration: 'none',
        }}
      >
        View Details <ExternalLink size={12} />
      </Link>
    </div>
  );
}
