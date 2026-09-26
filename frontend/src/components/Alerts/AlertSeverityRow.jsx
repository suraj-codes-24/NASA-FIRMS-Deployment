import React from 'react';
import { AlertCircle, Flame, Sun, ArrowDown } from 'lucide-react';

const SeverityCard = ({ title, count, color, icon, isSelected }) => (
  <div className="glass-panel" style={{ 
    flex: '1 1 200px', 
    padding: '12px 16px', 
    display: 'flex', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    backgroundColor: isSelected ? `${color}15` : undefined,
    borderTop: `3px solid ${isSelected ? color : 'var(--border-color)'}`,
    borderRadius: '4px',
    transition: 'all 0.2s ease',
    cursor: 'pointer'
  }}>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <span style={{ fontSize: '11px', color: isSelected ? color : 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{title}</span>
      <span style={{ fontSize: '24px', fontWeight: 700, color: 'white', lineHeight: 1 }}>{count}</span>
    </div>
    <div style={{ 
      backgroundColor: isSelected ? `${color}20` : 'rgba(255,255,255,0.03)', 
      padding: '8px', 
      borderRadius: '8px', 
      color: isSelected ? color : 'var(--text-secondary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {icon}
    </div>
  </div>
);

const AlertSeverityRow = ({ alerts = [] }) => {
  const getCount = (sev) => alerts.filter(a => {
      const frp = a.hotspot ? a.hotspot.frp : 0;
      if (sev === 'CRITICAL') return frp >= 100;
      if (sev === 'HIGH') return frp >= 50 && frp < 100;
      if (sev === 'MEDIUM') return frp >= 20 && frp < 50;
      if (sev === 'LOW') return frp < 20;
      return false;
  }).length;

  return (
    <div style={{ display: 'flex', gap: '1rem', width: '100%', flexWrap: 'wrap' }}>
      <SeverityCard title="Critical (FRP > 100)" count={getCount('CRITICAL')} color="#ef4444" icon={<AlertCircle size={24} />} isSelected={true} />
      <SeverityCard title="High (FRP > 50)" count={getCount('HIGH')} color="#ffa502" icon={<Flame size={24} />} isSelected={false} />
      <SeverityCard title="Medium (FRP > 20)" count={getCount('MEDIUM')} color="#eccc68" icon={<Sun size={24} />} isSelected={false} />
      <SeverityCard title="Low (FRP < 20)" count={getCount('LOW')} color="#1e90ff" icon={<ArrowDown size={24} />} isSelected={false} />
    </div>
  );
};

export default AlertSeverityRow;
