import React from 'react';

const SEVERITY_COLORS = {
  critical: { bg: 'rgba(231, 76, 60, 0.15)', text: '#e74c3c', border: 'rgba(231, 76, 60, 0.3)' },
  high:     { bg: 'rgba(230, 126, 34, 0.15)', text: '#e67e22', border: 'rgba(230, 126, 34, 0.3)' },
  medium:   { bg: 'rgba(234, 179, 8, 0.15)', text: '#eab308', border: 'rgba(234, 179, 8, 0.3)' },
  low:      { bg: 'rgba(46, 204, 113, 0.15)', text: '#2ecc71', border: 'rgba(46, 204, 113, 0.3)' },
};

const TYPE_COLORS = {
  'Industrial Fire':   { bg: 'rgba(231, 76, 60, 0.15)', text: '#e74c3c' },
  'Forest Fire':       { bg: 'rgba(230, 126, 34, 0.15)', text: '#e67e22' },
  'Gas Flare':         { bg: 'rgba(234, 179, 8, 0.15)', text: '#eab308' },
  'Agricultural Burn': { bg: 'rgba(46, 204, 113, 0.15)', text: '#2ecc71' },
  'Mining/Thermal':    { bg: 'rgba(52, 152, 219, 0.15)', text: '#3498db' },
  'Unclassified':      { bg: 'rgba(149, 165, 166, 0.15)', text: '#95a5a6' },
};

/**
 * Reusable Badge component for severity levels and classification types.
 * @param {'severity'|'type'} variant - The badge variant
 * @param {string} value - The display value (e.g., 'critical', 'Industrial Fire')
 * @param {string} size - 'sm' | 'md'
 */
const Badge = ({ variant = 'severity', value, size = 'sm' }) => {
  const lookup = variant === 'severity' ? SEVERITY_COLORS : TYPE_COLORS;
  const colors = lookup[value?.toLowerCase?.()] || lookup[value] || { bg: 'rgba(149,165,166,0.15)', text: '#95a5a6' };

  const padding = size === 'sm' ? '2px 8px' : '4px 12px';
  const fontSize = size === 'sm' ? '11px' : '12px';

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding,
      borderRadius: '20px',
      fontSize,
      fontWeight: 600,
      textTransform: 'capitalize',
      backgroundColor: colors.bg,
      color: colors.text,
      border: `1px solid ${colors.border || colors.bg}`,
      letterSpacing: '0.3px',
      lineHeight: 1.4,
      whiteSpace: 'nowrap',
    }}>
      {value}
    </span>
  );
};

export default Badge;
