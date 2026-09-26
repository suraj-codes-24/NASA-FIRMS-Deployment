import React, { useState } from 'react';
import SatelliteMap from '../components/Map/SatelliteMap';
import ClassificationDetails from '../components/Dashboard/ClassificationDetails';
import { Filter } from 'lucide-react';

const MapDashboard = () => {
  const [selectedHotspot, setSelectedHotspot] = useState(null);
  const [activeFilters, setActiveFilters] = useState([]); // Empty means ALL

  const filterOptions = [
    { label: 'All', value: 'ALL', color: 'rgba(255,255,255,0.1)' },
    { label: 'Industrial', value: 'Industrial Fire', color: '#ef4444' },
    { label: 'Gas Flare', value: 'Gas Flare', color: '#eab308' },
    { label: 'Vegetation', value: 'Forest Fire', color: '#f97316' },
    { label: 'Agricultural', value: 'Agricultural Burn', color: '#10b981' }
  ];

  return (
    <div style={{ height: '100%', width: '100%', position: 'relative', overflow: 'hidden' }}>
      <SatelliteMap 
        activeFilters={activeFilters} 
        onFilterChange={setActiveFilters} 
        selectedHotspot={selectedHotspot} 
        onSelectHotspot={setSelectedHotspot} 
      />
      <ClassificationDetails hotspot={selectedHotspot} onClose={() => setSelectedHotspot(null)} />
    </div>
  );
};

export default MapDashboard;
