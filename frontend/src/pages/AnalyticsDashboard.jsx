import React, { useState, useEffect } from 'react';
import { Key } from 'lucide-react';
import StatCards from '../components/analytics/StatCards';
import FilterPanel from '../components/analytics/FilterPanel';
import HeatMap from '../components/analytics/HeatMap';
import RecentAlertsTimeline from '../components/analytics/RecentAlertsTimeline';
import FrequencyChart from '../components/analytics/FrequencyChart';

const AnalyticsDashboard = () => {
  const [filters, setFilters] = useState({
    date_from: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    date_to: new Date().toISOString().split('T')[0],
    ml_label: '',
    min_confidence: 75,
    region: 'global'
  });

  return (
    <div style={{ 
      height: '100%', 
      width: '100%', 
      padding: '24px 32px', 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '24px', 
      overflowY: 'auto',
      backgroundColor: 'var(--bg-base)'
    }}>
      

      {/* Top Stats */}
      <StatCards filters={filters} />

      {/* Main Grid: Filters, Map, Alerts */}
      <div style={{ flex: 1, display: 'flex', gap: '24px', minHeight: '400px' }}>
        <FilterPanel filters={filters} setFilters={setFilters} />
        <HeatMap filters={filters} />
        <RecentAlertsTimeline />
      </div>
      
      {/* Bottom Chart */}
      <FrequencyChart filters={filters} />
      
    </div>
  );
};

export default AnalyticsDashboard;
