import React, { useState, useEffect } from 'react';
import { Flame, Factory, TreePine, Droplets, AlertTriangle, Pickaxe, Loader2 } from 'lucide-react';
import { fetchAnalyticsSummary, fetchAnalyticsClassification } from '../../api';

const StatCard = ({ title, value, icon, color, loading }) => (
  <div 
    className="glass-panel" 
    style={{ 
      flex: '1 1 200px', 
      padding: '12px 16px', 
      display: 'flex', 
      justifyContent: 'space-between',
      alignItems: 'center', 
      borderTop: `3px solid ${color}`,
      background: 'rgba(255,255,255,0.02)',
      borderRadius: '4px',
      boxShadow: `0 4px 20px ${color}15`,
      transition: 'transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s',
      cursor: 'default'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-2px)';
      e.currentTarget.style.boxShadow = `0 6px 25px ${color}30`;
      e.currentTarget.style.backgroundColor = `${color}15`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'none';
      e.currentTarget.style.boxShadow = `0 4px 20px ${color}15`;
      e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.02)';
    }}
  >
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <span style={{ fontSize: '11px', color: color, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{title}</span>
      <span style={{ fontSize: '24px', fontWeight: 700, color: 'white', lineHeight: 1, display: 'flex', alignItems: 'center', gap: '8px' }}>
        {value !== null ? value.toLocaleString() : '—'}
        {loading && <Loader2 size={16} color="var(--text-muted)" className="spin" />}
      </span>
    </div>
    <div style={{ 
      backgroundColor: `${color}20`, 
      padding: '8px', 
      borderRadius: '8px', 
      color: color,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {icon}
    </div>
  </div>
);

const StatCards = ({ filters }) => {
  const [stats, setStats] = useState({
    total: null,
    mining: null,
    agri: null,
    gasFlare: null,
    alerts: null,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        // Strip out empty filters to avoid passing empty strings
        const activeFilters = {};
        if (filters.date_from) activeFilters.date_from = filters.date_from;
        if (filters.date_to) activeFilters.date_to = filters.date_to;
        if (filters.ml_label) activeFilters.ml_label = filters.ml_label;
        if (filters.min_confidence > 0) activeFilters.min_confidence = filters.min_confidence;

        const [summary, classes] = await Promise.all([
          fetchAnalyticsSummary(activeFilters),
          fetchAnalyticsClassification(activeFilters),
        ]);

        const getCount = (label) => {
          const item = classes.find(c => c.label === label);
          return item ? item.count : 0;
        };

        setStats({
          total: summary.total_hotspots,
          mining: getCount('Mining/Thermal') || getCount('MINING_THERMAL'),
          agri: getCount('Agricultural Burn') || getCount('AGRICULTURAL_BURN'),
          gasFlare: getCount('Gas Flare') || getCount('GAS_FLARE'),
          alerts: summary.high_severity_alerts,
        });
      } catch (err) {
        console.error('Failed to load stat cards:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, [filters]);

  return (
    <div style={{ display: 'flex', gap: '1rem', width: '100%', marginBottom: '1rem', flexWrap: 'wrap' }}>
      <StatCard title="Total Anomalies" value={stats.total} icon={<Flame size={24} />} color="#ef4444" loading={loading} />
      <StatCard title="Mining & Thermal" value={stats.mining} icon={<Pickaxe size={24} />} color="#3b82f6" loading={loading} />
      <StatCard title="Agricultural Burn" value={stats.agri} icon={<TreePine size={24} />} color="#10b981" loading={loading} />
      <StatCard title="Gas Flares" value={stats.gasFlare} icon={<Droplets size={24} />} color="#eab308" loading={loading} />
      <StatCard title="High Sev Alerts" value={stats.alerts} icon={<AlertTriangle size={24} />} color="#ef4444" loading={loading} />
    </div>
  );
};

export default StatCards;
