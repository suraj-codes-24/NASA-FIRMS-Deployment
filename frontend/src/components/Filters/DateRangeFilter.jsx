import React from 'react';
import { Calendar } from 'lucide-react';

const inputStyle = {
  width: '100%',
  padding: '6px 10px',
  borderRadius: '8px',
  border: '1px solid rgba(255,255,255,0.1)',
  backgroundColor: 'rgba(255,255,255,0.05)',
  color: 'white',
  fontSize: '12px',
};

const DateRangeFilter = ({ dateFrom, dateTo, onChange }) => (
  <div>
    <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
      <Calendar size={14} /> Date Range
    </label>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <input
        type="date"
        value={dateFrom || ''}
        onChange={(e) => onChange(e.target.value, dateTo)}
        style={inputStyle}
        placeholder="From"
      />
      <input
        type="date"
        value={dateTo || ''}
        onChange={(e) => onChange(dateFrom, e.target.value)}
        style={inputStyle}
        placeholder="To"
      />
    </div>
  </div>
);

export default DateRangeFilter;
