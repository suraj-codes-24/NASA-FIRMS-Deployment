import React, { useState, useEffect } from 'react';
import { fetchAlerts } from '../../api';

const AlertItem = ({ date, time, title, subtitle, color, number, isLast }) => (
  <div style={{ display: 'flex', gap: '15px', position: 'relative', marginBottom: isLast ? '0' : '20px' }}>
    {/* Line connector */}
    {!isLast && (
      <div style={{ position: 'absolute', left: '11px', top: '24px', bottom: '-20px', width: '2px', backgroundColor: 'rgba(255,255,255,0.05)' }}></div>
    )}
    
    <div style={{ 
      width: '24px', height: '24px', borderRadius: '50%', border: `2px solid ${color}`, 
      display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', 
      fontWeight: 'bold', color: color, backgroundColor: 'var(--bg-card)', zIndex: 2,
      boxShadow: `0 0 10px ${color}40`
    }}>
      {number}
    </div>
    
    <div style={{ 
      flex: 1, backgroundColor: `${color}10`, border: `1px solid ${color}30`, 
      borderRadius: '8px', padding: '10px 14px',
      transition: 'background-color 0.2s',
      cursor: 'default'
    }}
    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = `${color}20`}
    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = `${color}10`}
    >
      <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>{date}, {time}</div>
      <div style={{ fontSize: '13px', fontWeight: 500, color: 'white', marginBottom: '4px', letterSpacing: '0.3px' }}>{title}</div>
      <div style={{ fontSize: '11px', color: color, fontWeight: 500 }}>[{subtitle}]</div>
    </div>
  </div>
);

const RecentAlertsTimeline = () => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const data = await fetchAlerts();
        // Take top 5 recent alerts
        setAlerts(data.slice(0, 5));
      } catch (err) {
        console.error("Failed to fetch alerts for timeline:", err);
      }
    };
    
    loadAlerts();
    const interval = setInterval(loadAlerts, 15000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity) => {
    if (severity === 'CRITICAL') return '#ef4444';
    if (severity === 'HIGH') return '#ffa502';
    if (severity === 'MEDIUM') return '#eab308';
    return '#10b981';
  };

  const formatType = (type) => {
    return type.replace(/_/g, ' ');
  };

  return (
    <div className="glass-panel" style={{ width: '300px', display: 'flex', flexDirection: 'column', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 600, letterSpacing: '0.5px', color: '#fff' }}>Recent Alerts</h3>
        {alerts.length > 0 && (
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444', boxShadow: '0 0 8px #ef4444' }}></span>
        )}
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', paddingRight: '5px' }} className="custom-scrollbar">
        {alerts.length === 0 ? (
          <div style={{ fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px' }}>
            No recent alerts.
          </div>
        ) : (
          alerts.map((alert, index) => {
            const dateObj = new Date(alert.created_at);
            const dateStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const timeStr = dateObj.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
            
            return (
              <AlertItem 
                key={alert.id}
                number={index + 1}
                date={dateStr} 
                time={timeStr} 
                title={formatType(alert.alert_type)} 
                subtitle={`${alert.severity} Severity`} 
                color={getSeverityColor(alert.severity)}
                isLast={index === alerts.length - 1}
              />
            );
          })
        )}
      </div>
    </div>
  );
};

export default RecentAlertsTimeline;
