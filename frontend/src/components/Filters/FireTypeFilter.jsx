import React from 'react';
import { Flame } from 'lucide-react';

const FIRE_TYPES = [
  { value: null, label: 'All Types', color: '#ffffff' },
  { value: 'Industrial Fire', label: 'Industrial Fire', color: '#e74c3c' },
  { value: 'Forest Fire', label: 'Forest Fire', color: '#e67e22' },
  { value: 'Gas Flare', label: 'Gas Flare', color: '#eab308' },
  { value: 'Agricultural Burn', label: 'Agricultural Burn', color: '#2ecc71' },
  { value: 'Mining/Thermal', label: 'Mining / Thermal', color: '#3498db' },
  { value: 'Unclassified', label: 'Unclassified', color: '#95a5a6' },
];

const FireTypeFilter = ({ selected, onChange }) => (
  <div>
    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
      <Flame size={14} /> Fire Type
    </label>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {FIRE_TYPES.map((type) => (
        <button
          key={type.label}
          onClick={() => onChange(type.value)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 10px',
            borderRadius: '8px',
            border: selected === type.value ? `1px solid ${type.color}44` : '1px solid transparent',
            backgroundColor: selected === type.value ? `${type.color}15` : 'transparent',
            color: selected === type.value ? type.color : 'var(--text-secondary)',
            fontSize: '12px',
            cursor: 'pointer',
            textAlign: 'left',
            transition: 'all 0.15s ease',
          }}
        >
          <span style={{
            width: '8px', height: '8px', borderRadius: '50%',
            backgroundColor: type.color, flexShrink: 0,
          }} />
          {type.label}
        </button>
      ))}
    </div>
  </div>
);

export default FireTypeFilter;
