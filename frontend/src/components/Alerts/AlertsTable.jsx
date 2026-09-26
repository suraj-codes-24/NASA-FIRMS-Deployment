import React, { useState } from 'react';
import { MapPin, AlertCircle, CheckCircle, Clock, ArrowDown, ArrowUpDown } from 'lucide-react';

const getTypeStyle = (type) => {
  if (type === 'Industrial Fire' || type === 'INDUSTRIAL_FIRE') return { bg: 'rgba(239, 68, 68, 0.15)', border: 'rgba(239, 68, 68, 0.3)', color: '#ef4444' };
  if (type === 'Forest Fire' || type === 'FOREST_FIRE') return { bg: 'rgba(249, 115, 22, 0.15)', border: 'rgba(249, 115, 22, 0.3)', color: '#f97316' };
  if (type === 'Gas Flare' || type === 'GAS_FLARE') return { bg: 'rgba(234, 179, 8, 0.15)', border: 'rgba(234, 179, 8, 0.3)', color: '#eab308' };
  if (type === 'Agricultural Burn' || type === 'AGRICULTURAL_BURN') return { bg: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.3)', color: '#10b981' };
  if (type === 'Mining Activity' || type === 'Mining/Thermal' || type === 'MINING_THERMAL') return { bg: 'rgba(59, 130, 246, 0.15)', border: 'rgba(59, 130, 246, 0.3)', color: '#3b82f6' };
  return { bg: 'rgba(156, 163, 175, 0.15)', border: 'rgba(156, 163, 175, 0.3)', color: '#9ca3af' };
};

const getStatusBadge = (status) => {
  if (status === 'RESOLVED') return { bg: 'rgba(46, 213, 115, 0.15)', color: '#2ed573', icon: <CheckCircle size={12} /> };
  if (status === 'ACKNOWLEDGED') return { bg: 'rgba(30, 144, 255, 0.15)', color: '#1e90ff', icon: <Clock size={12} /> };
  return { bg: 'rgba(255, 165, 2, 0.15)', color: '#ffa502', icon: <AlertCircle size={12} /> }; // NEW
};

const AlertsTable = ({ alerts = [], selectedAlert, onSelectAlert }) => {
  const [hoveredRow, setHoveredRow] = useState(null);

  const SortIcon = ({ active }) => (
    active 
      ? <ArrowDown size={14} color="#1e90ff" strokeWidth={3} />
      : <ArrowUpDown size={14} color="rgba(255,255,255,0.15)" strokeWidth={2} />
  );

  const headerStyle = { 
    padding: '16px 12px', 
    borderRight: '1px solid rgba(255,255,255,0.05)',
    borderBottom: '2px solid rgba(30, 144, 255, 0.2)',
    cursor: 'pointer',
    position: 'sticky',
    top: 0,
    backgroundColor: '#161922', // completely solid to prevent scroll bleed
    zIndex: 10
  };
  
  const cellStyle = { 
    padding: '16px 12px', 
    borderRight: '1px solid rgba(255,255,255,0.05)' 
  };

  const formatLocation = (hotspot) => {
    if (!hotspot || !hotspot.nearest_facility) return 'Remote Location';
    const f = hotspot.nearest_facility;
    
    // Check if string is predominantly English/ASCII
    const isEnglish = (str) => {
      if (!str) return false;
      const stripped = str.replace(/\s+/g, '');
      if (stripped.length === 0) return false;
      const nonAsciiCount = (stripped.match(/[^\x00-\x7F]/g) || []).length;
      return (nonAsciiCount / stripped.length) < 0.5;
    };

    let locationPart = 'Industrial Facility';
    if (f.name && isEnglish(f.name)) {
      locationPart = f.name;
    } else if (f.district && isEnglish(f.district)) {
      locationPart = f.district;
    } else if (f.state && isEnglish(f.state)) {
      locationPart = f.state;
    }
    
    return `${locationPart}, India`;
  };

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '0 20px', margin: '0 -20px' }}>
      <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, textAlign: 'left', fontSize: '13px', borderTop: '1px solid rgba(255,255,255,0.05)', borderLeft: '1px solid rgba(255,255,255,0.05)', borderRight: '1px solid rgba(255,255,255,0.05)' }}>
        <thead>
          <tr style={{ color: '#a4b0be', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>
            <th style={headerStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>Alert ID <SortIcon /></div>
            </th>
            <th style={headerStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>Type <SortIcon /></div>
            </th>
            <th style={{ ...headerStyle, cursor: 'default' }}>Location</th>
            <th style={headerStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>State (Country) <SortIcon /></div>
            </th>
            <th style={headerStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>FRP <SortIcon /></div>
            </th>
            <th style={headerStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>Confidence (%) <SortIcon /></div>
            </th>
            <th style={headerStyle}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'white' }}>Date / Time <SortIcon active /></div>
            </th>
            <th style={{ ...headerStyle, borderRight: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>Status <SortIcon /></div>
            </th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert, index) => {
            const isSelected = selectedAlert && selectedAlert.id === alert.id;
            const isHovered = hoveredRow === index;
            const isEven = index % 2 === 0;
            const type = alert.hotspot ? alert.hotspot.ml_label : 'Unknown';
            const typeStyle = getTypeStyle(type);
            const statusStyle = getStatusBadge(alert.status);
            const time = new Date(alert.created_at).toLocaleString([], {month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'});
            const confidence = alert.hotspot ? alert.hotspot.confidence : 0;
            
            return (
              <tr key={index} 
                onClick={() => onSelectAlert && onSelectAlert(alert)}
                onMouseEnter={() => setHoveredRow(index)}
                onMouseLeave={() => setHoveredRow(null)}
                style={{ 
                  borderBottom: '1px solid rgba(255,255,255,0.05)', 
                  backgroundColor: isSelected ? 'rgba(30, 144, 255, 0.15)' : (isHovered ? 'rgba(255,255,255,0.05)' : (isEven ? 'rgba(255,255,255,0.02)' : 'transparent')),
                  cursor: 'pointer',
                  transition: 'background-color 0.2s ease'
              }}>
                <td style={{ ...cellStyle, fontWeight: 600, color: isSelected ? '#1e90ff' : 'white', letterSpacing: '0.5px' }}>
                  AFD-{alert.id}
                </td>
                <td style={cellStyle}>
                  <span style={{ 
                    padding: '6px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600, letterSpacing: '0.5px',
                    backgroundColor: typeStyle.bg, border: `1px solid ${typeStyle.border}`, color: typeStyle.color,
                    whiteSpace: 'nowrap'
                  }}>
                    {type}
                  </span>
                </td>
                <td style={{ ...cellStyle, color: 'var(--text-secondary)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={12} color="var(--text-muted)" />
                    <span style={{ fontFamily: 'monospace', color: '#eccc68' }}>
                      {alert.hotspot ? `${alert.hotspot.latitude.toFixed(4)}, ${alert.hotspot.longitude.toFixed(4)}` : 'Unknown'}
                    </span>
                  </div>
                </td>
                <td style={{ ...cellStyle, color: 'var(--text-secondary)' }}>
                  {formatLocation(alert.hotspot)}
                </td>
                <td style={{ ...cellStyle, fontWeight: 500, color: alert.hotspot && alert.hotspot.frp > 100 ? '#ef4444' : 'white' }}>
                  {alert.hotspot ? alert.hotspot.frp : '-'}
                </td>
                <td style={cellStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '50px', height: '4px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ width: `${confidence}%`, height: '100%', backgroundColor: confidence > 90 ? '#2ed573' : (confidence > 70 ? '#ffa502' : '#ef4444') }}></div>
                    </div>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>{confidence}%</span>
                  </div>
                </td>
                <td style={{ ...cellStyle, color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>{time}</td>
                <td style={{ ...cellStyle, borderRight: 'none' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: statusStyle.color, backgroundColor: statusStyle.bg, padding: '6px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600, letterSpacing: '0.5px', width: 'fit-content' }}>
                    {statusStyle.icon} {alert.status}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default AlertsTable;
