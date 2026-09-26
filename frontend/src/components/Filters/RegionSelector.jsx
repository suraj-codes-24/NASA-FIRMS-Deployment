import React from 'react';
import { MapPin } from 'lucide-react';

const REGIONS = [
  { value: null, label: 'All India' },
  { value: '68.0,6.0,77.5,23.5', label: 'Western India' },
  { value: '77.5,6.0,87.0,23.5', label: 'Southern India' },
  { value: '77.5,23.5,87.0,37.5', label: 'Northern India' },
  { value: '87.0,6.0,97.5,37.5', label: 'Eastern India' },
  { value: '72.0,18.0,74.0,20.0', label: 'Mumbai Region' },
  { value: '76.5,28.0,78.0,29.5', label: 'Delhi NCR' },
  { value: '87.5,21.5,88.5,23.0', label: 'Kolkata Region' },
  { value: '79.5,12.5,81.0,14.0', label: 'Chennai Region' },
];

const RegionSelector = ({ selected, onChange }) => (
  <div>
    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
      <MapPin size={14} /> Region
    </label>
    <select
      value={selected || ''}
      onChange={(e) => onChange(e.target.value || null)}
      style={{
        width: '100%',
        padding: '8px 10px',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.1)',
        backgroundColor: 'rgba(255,255,255,0.05)',
        color: 'white',
        fontSize: '12px',
        cursor: 'pointer',
      }}
    >
      {REGIONS.map((r) => (
        <option key={r.label} value={r.value || ''} style={{ backgroundColor: '#1a1f3a' }}>
          {r.label}
        </option>
      ))}
    </select>
  </div>
);

export default RegionSelector;
