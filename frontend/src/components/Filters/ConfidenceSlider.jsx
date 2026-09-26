import React from 'react';
import { SlidersHorizontal } from 'lucide-react';

const ConfidenceSlider = ({ value = 0, onChange }) => (
  <div>
    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
      <SlidersHorizontal size={14} /> Min Confidence
    </label>
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <input
        type="range"
        min="0"
        max="100"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{
          flex: 1,
          accentColor: '#e74c3c',
          height: '4px',
        }}
      />
      <span style={{
        minWidth: '36px',
        textAlign: 'right',
        fontSize: '12px',
        fontWeight: 600,
        color: value >= 70 ? '#2ecc71' : value >= 40 ? '#eab308' : '#e74c3c',
      }}>
        {value}%
      </span>
    </div>
  </div>
);

export default ConfidenceSlider;
