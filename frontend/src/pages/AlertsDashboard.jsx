import React, { useState, useEffect } from 'react';
import AlertSeverityRow from '../components/alerts/AlertSeverityRow';
import AlertsTable from '../components/alerts/AlertsTable';
import AlertDetailPane from '../components/alerts/AlertDetailPane';
import { fetchAlerts, acknowledgeAlert, resolveAlert, saveAlertNotes } from '../api';

const AlertsDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  
  // Filter States
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('All Types');
  const [severityFilter, setSeverityFilter] = useState('All Severities');
  const [dateRange, setDateRange] = useState('');

  const loadAlerts = async () => {
    try {
      const data = await fetchAlerts();
      setAlerts(data);
    } catch (err) {
      console.error("Failed to fetch alerts:", err);
    }
  };

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 15000); // 15s refresh
    return () => clearInterval(interval);
  }, []);

  // Update selected alert if its status changes during a refresh
  useEffect(() => {
    if (selectedAlert) {
      const updated = alerts.find(a => a.id === selectedAlert.id);
      if (updated) setSelectedAlert(updated);
    }
  }, [alerts]);

  const handleAction = async (action, note = "") => {
    if (!selectedAlert) return;
    try {
      if (action === 'acknowledge') {
        await acknowledgeAlert(selectedAlert.id);
        if (note) await saveAlertNotes(selectedAlert.id, note);
      } else if (action === 'resolve') {
        await resolveAlert(selectedAlert.id, note);
      } else if (action === 'save_notes') {
        await saveAlertNotes(selectedAlert.id, note);
      }
      await loadAlerts(); // Refresh list immediately
    } catch (err) {
      console.error("Action failed:", err);
    }
  };

  // Compute filtered alerts
  const filteredAlerts = alerts.filter(alert => {
    // Search Term matching
    const matchesSearch = searchTerm === '' || 
      `AFD-${alert.id}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (alert.hotspot && alert.hotspot.ml_label && alert.hotspot.ml_label.toLowerCase().includes(searchTerm.toLowerCase()));
      
    // Type matching
    const matchesType = typeFilter === 'All Types' || 
      (alert.hotspot && alert.hotspot.ml_label === typeFilter);
      
    // Severity matching (assuming Status mapping for now since we don't have severity)
    const matchesSeverity = severityFilter === 'All Severities' || alert.status === severityFilter;

    // Date Range (simple string match for now)
    const timeStr = new Date(alert.created_at).toLocaleDateString();
    const matchesDate = dateRange === '' || timeStr.includes(dateRange);

    return matchesSearch && matchesType && matchesSeverity && matchesDate;
  });

  const handleGenerateReport = () => {
    if (filteredAlerts.length === 0) return;
    
    const headers = ['Alert ID', 'Type', 'Latitude', 'Longitude', 'FRP', 'Confidence', 'Time', 'Status'];
    const rows = filteredAlerts.map(a => [
      `AFD-${a.id}`,
      a.hotspot ? a.hotspot.ml_label : 'Unknown',
      a.hotspot ? a.hotspot.latitude : '',
      a.hotspot ? a.hotspot.longitude : '',
      a.hotspot ? a.hotspot.frp : '',
      a.hotspot ? a.hotspot.confidence : '',
      new Date(a.created_at).toLocaleString(),
      a.status
    ]);
    
    const csvContent = headers.join(',') + '\n' 
      + rows.map(e => e.map(val => `"${val}"`).join(',')).join('\n');
      
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `live_alerts_report_${new Date().getTime()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ height: '100%', width: '100%', padding: '20px', boxSizing: 'border-box', display: 'flex', gap: '20px', overflow: 'hidden' }}>
      
      {/* Left Main Content */}
      <div style={{ flex: 1, display: selectedAlert ? 'none' : 'flex', flexDirection: 'column', gap: '12px', minWidth: 0 }}>
        
        {/* Severity Breakdown */}
        <AlertSeverityRow alerts={filteredAlerts} />

        {/* Filter Bar */}
        <div className="glass-panel" style={{ padding: '12px 20px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          
          {/* Search */}
          <div style={{ display: 'flex', alignItems: 'center', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0 12px', flex: 1, minWidth: '200px' }}>
            <span style={{ color: 'var(--text-muted)' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </span>
            <input type="text" placeholder="Search Alerts (ID, Type)..." 
              value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
              style={{ 
                width: '100%', backgroundColor: 'transparent', border: 'none', 
                color: 'white', padding: '8px 10px', outline: 'none', fontSize: '12px'
            }} />
          </div>
          
          {/* Filters */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <select 
              value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
              style={{ 
                backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', 
                borderRadius: '8px', color: 'var(--text-primary)', padding: '8px 12px', outline: 'none', fontSize: '12px', colorScheme: 'dark', cursor: 'pointer' 
             }}>
               <option value="All Types" style={{background: 'var(--bg-card)'}}>All Types</option>
               <option value="Industrial Fire" style={{background: 'var(--bg-card)'}}>Industrial Fire</option>
               <option value="Gas Flare" style={{background: 'var(--bg-card)'}}>Gas Flare</option>
               <option value="Forest Fire" style={{background: 'var(--bg-card)'}}>Forest Fire</option>
               <option value="Agricultural Burn" style={{background: 'var(--bg-card)'}}>Agricultural Burn</option>
               <option value="Mining Activity" style={{background: 'var(--bg-card)'}}>Mining Activity</option>
             </select>

            <select 
              value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}
              style={{ 
                backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', 
                borderRadius: '8px', color: 'var(--text-primary)', padding: '8px 12px', outline: 'none', fontSize: '12px', colorScheme: 'dark', cursor: 'pointer' 
             }}>
               <option value="All Severities" style={{background: 'var(--bg-card)'}}>All Statuses</option>
               <option value="NEW" style={{background: 'var(--bg-card)'}}>NEW</option>
               <option value="ACKNOWLEDGED" style={{background: 'var(--bg-card)'}}>ACKNOWLEDGED</option>
               <option value="RESOLVED" style={{background: 'var(--bg-card)'}}>RESOLVED</option>
             </select>

            <input type="date" 
               value={dateRange} onChange={(e) => setDateRange(e.target.value)}
               style={{ 
                 backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', 
                 borderRadius: '8px', color: 'var(--text-primary)', padding: '7px 12px', outline: 'none', fontSize: '12px', colorScheme: 'dark', cursor: 'pointer' 
             }} />
          </div>

          <button onClick={handleGenerateReport} style={{ 
            display: 'flex', alignItems: 'center', gap: '8px', height: '32px', padding: '0 12px', 
            borderRadius: '8px', background: 'rgba(30, 144, 255, 0.1)', border: '1px solid rgba(30, 144, 255, 0.3)',
            color: '#1e90ff', fontWeight: 600, cursor: 'pointer', fontSize: '11px', letterSpacing: '0.5px'
          }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            EXPORT CSV
          </button>
        </div>

        {/* Alerts Table */}
        <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px 0', overflow: 'hidden' }}>
          <h4 style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.5px', marginBottom: '16px', paddingLeft: '20px' }}>RECENT ALERTS</h4>
          <AlertsTable alerts={filteredAlerts} selectedAlert={selectedAlert} onSelectAlert={setSelectedAlert} />
        </div>

      </div>

      {/* Right Details Pane */}
      {selectedAlert && (
        <AlertDetailPane selectedAlert={selectedAlert} onAction={handleAction} onClose={() => setSelectedAlert(null)} />
      )}
      
    </div>
  );
};

export default AlertsDashboard;
