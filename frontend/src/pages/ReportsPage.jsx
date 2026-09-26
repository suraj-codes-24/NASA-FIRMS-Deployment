import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Filter, Database, AlertCircle, Loader2 } from 'lucide-react';
import { fetchReportSummary, generateReport } from '../api';

export default function ReportsPage() {
  const [summary, setSummary] = useState({
    total_hotspots: 0,
    industrial_fires: 0,
    open_alerts: 0,
    report_available: false
  });
  
  const [filters, setFilters] = useState({
    date_from: '',
    date_to: '',
    ml_label: ''
  });
  
  const [generating, setGenerating] = useState(false);
  const [lastGeneratedTime, setLastGeneratedTime] = useState(null);

  useEffect(() => {
    const loadSummary = async () => {
      try {
        const data = await fetchReportSummary();
        setSummary(data);
      } catch (err) {
        console.error("Failed to load report summary", err);
      }
    };
    loadSummary();
  }, []);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setLastGeneratedTime(null);
    try {
      // Clean up empty filters
      const activeFilters = {};
      if (filters.date_from) activeFilters.date_from = filters.date_from;
      if (filters.date_to) activeFilters.date_to = filters.date_to;
      if (filters.ml_label) activeFilters.ml_label = filters.ml_label;

      const blob = await generateReport(activeFilters);
      
      // Programmatically download the file
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ignis_report_${new Date().toISOString().slice(0,10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      
      setLastGeneratedTime(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Report generation failed:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ height: '100%', width: '100%', padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
      
      {/* Header */}
      <div>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
          Configure, generate, and export classified hotspot and anomaly data for offline analysis.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
        
        {/* Left Col: Export Configuration */}
        <div className="glass-panel" style={{ flex: '1 1 500px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={20} color="var(--text-secondary)" /> Report Configuration
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>Date From</label>
                <input 
                  type="date" 
                  name="date_from"
                  value={filters.date_from}
                  onChange={handleFilterChange}
                  style={{ width: '100%', colorScheme: 'dark', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)', padding: '10px 14px', outline: 'none', fontSize: '13px' }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>Date To</label>
                <input 
                  type="date" 
                  name="date_to"
                  value={filters.date_to}
                  onChange={handleFilterChange}
                  style={{ width: '100%', colorScheme: 'dark', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)', padding: '10px 14px', outline: 'none', fontSize: '13px' }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>Classification Type</label>
              <select 
                name="ml_label"
                value={filters.ml_label}
                onChange={handleFilterChange}
                style={{ width: '100%', colorScheme: 'dark', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--text-primary)', padding: '10px 14px', outline: 'none', fontSize: '13px' }}
              >
                <option value="" style={{background: 'var(--bg-card)'}}>All Classifications</option>
                <option value="Industrial Fire" style={{background: 'var(--bg-card)'}}>Industrial Fire</option>
                <option value="Forest Fire" style={{background: 'var(--bg-card)'}}>Forest Fire</option>
                <option value="Gas Flare" style={{background: 'var(--bg-card)'}}>Gas Flare</option>
                <option value="Agricultural Burn" style={{background: 'var(--bg-card)'}}>Agricultural Burn</option>
                <option value="Mining/Thermal" style={{background: 'var(--bg-card)'}}>Mining/Thermal</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
            <button
              onClick={handleGenerate}
              disabled={generating}
              style={{ 
                width: '100%', padding: '12px', fontSize: '15px', fontWeight: 600, borderRadius: '8px', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                background: 'linear-gradient(135deg, #00a8ff, #3742fa)',
                color: '#fff', border: 'none', cursor: generating ? 'wait' : 'pointer'
              }}
            >
              {generating ? <><Loader2 size={20} className="spin" /> Generating Data Payload…</> : <><Download size={20} /> Generate & Download CSV</>}
            </button>
            
            {lastGeneratedTime && (
              <div style={{ marginTop: '12px', fontSize: '13px', color: '#2ed573', textAlign: 'center' }}>
                ✓ Report successfully exported at {lastGeneratedTime}
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Database Summary */}
        <div style={{ flex: '1 1 350px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Database size={20} color="var(--text-secondary)" /> Database Summary
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: 'var(--bg-main)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Total Anomalies Logged</span>
                <span style={{ fontSize: '18px', fontWeight: 600 }}>{summary.total_hotspots.toLocaleString()}</span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: 'rgba(239, 68, 68, 0.05)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Industrial Fires Detected</span>
                <span style={{ fontSize: '18px', fontWeight: 600, color: '#ef4444' }}>{summary.industrial_fires.toLocaleString()}</span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: 'rgba(255, 165, 2, 0.05)', borderRadius: '8px', border: '1px solid rgba(255, 165, 2, 0.2)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Open Alerts Requires Review</span>
                <span style={{ fontSize: '18px', fontWeight: 600, color: '#ffa502' }}>{summary.open_alerts.toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px', flex: 1 }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={20} color="var(--text-secondary)" /> Data Compliance
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              All exported CSV files contain classified NTRO intelligence. Reports must be handled according to strict internal security protocols. 
              Data retention policies mandate that unverified hotspot logs older than 90 days are automatically archived.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}
