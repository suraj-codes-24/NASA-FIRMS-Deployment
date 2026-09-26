/**
 * Dashboard/StatCard.jsx
 * 
 * Individual stat card component for the dashboard.
 * Spec §9.3 requires Dashboard/StatCard.jsx.
 */
import React from 'react';

const StatCard = ({ title, value, icon, color = '#e74c3c', trend = null }) => (
  <div className="glass-panel" style={{
    padding: '16px 20px',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '14px',
    flex: 1,
    minWidth: '180px',
  }}>
    <div style={{
      width: '42px',
      height: '42px',
      borderRadius: '10px',
      backgroundColor: `${color}20`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: color,
      fontSize: '20px',
      flexShrink: 0,
    }}>
      {icon}
    </div>
    <div>
      <div style={{
        fontSize: '12px',
        color: 'var(--text-secondary)',
        fontWeight: 500,
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
      }}>
        {title}
      </div>
      <div style={{
        fontSize: '22px',
        fontWeight: 700,
        color: 'white',
        lineHeight: 1.2,
      }}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {trend !== null && (
        <div style={{
          fontSize: '11px',
          color: trend >= 0 ? '#2ecc71' : '#e74c3c',
          fontWeight: 600,
          marginTop: '2px',
        }}>
          {trend >= 0 ? '▲' : '▼'} {Math.abs(trend)}%
        </div>
      )}
    </div>
  </div>
);

export default StatCard;
