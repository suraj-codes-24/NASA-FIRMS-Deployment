import React from 'react';
import DateRangeFilter from './DateRangeFilter';
import FireTypeFilter from './FireTypeFilter';
import ConfidenceSlider from './ConfidenceSlider';
import RegionSelector from './RegionSelector';
import { Filter, X } from 'lucide-react';

/**
 * FilterSidebar — collapsible filter panel for the Map dashboard.
 * Composes the four filter sub-components defined in the spec.
 */
const FilterSidebar = ({ filters, onChange, onReset, isOpen, onToggle }) => {
  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="filter-sidebar" style={{
      width: isOpen ? '280px' : '0px',
      minWidth: isOpen ? '280px' : '0px',
      overflow: 'hidden',
      transition: 'all 0.3s ease',
      borderRight: isOpen ? '1px solid rgba(255,255,255,0.06)' : 'none',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: 'white', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} /> Filters
          </h3>
          <button onClick={onToggle} style={{
            background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px',
          }}>
            <X size={16} />
          </button>
        </div>

        {/* Filter Components */}
        <DateRangeFilter
          dateFrom={filters.dateFrom}
          dateTo={filters.dateTo}
          onChange={(from, to) => onChange({ ...filters, dateFrom: from, dateTo: to })}
        />

        <FireTypeFilter
          selected={filters.fireType}
          onChange={(type) => handleChange('fireType', type)}
        />

        <ConfidenceSlider
          value={filters.confidenceMin}
          onChange={(val) => handleChange('confidenceMin', val)}
        />

        <RegionSelector
          selected={filters.region}
          onChange={(region) => handleChange('region', region)}
        />

        {/* Reset */}
        <button onClick={onReset} style={{
          padding: '8px 16px',
          borderRadius: '8px',
          border: '1px solid rgba(255,255,255,0.1)',
          background: 'rgba(255,255,255,0.05)',
          color: 'var(--text-secondary)',
          fontSize: '12px',
          cursor: 'pointer',
          marginTop: 'auto',
        }}>
          Reset All Filters
        </button>
      </div>
    </div>
  );
};

export default FilterSidebar;
