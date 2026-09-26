import React, { useState } from 'react';

const FilterPanel = ({ filters, setFilters }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="glass-panel" style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      
      {/* Date Range */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h4 style={{ fontSize: '13px', color: '#fff', fontWeight: 500, letterSpacing: '0.5px' }}>Date Range</h4>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', width: '30px' }}>FROM</span>
            <input 
              type="date" 
              name="date_from"
              value={filters.date_from}
              onChange={handleChange}
              style={{ flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: 'white', padding: '8px 10px', fontSize: '12px', outline: 'none', colorScheme: 'dark' }} 
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', width: '30px' }}>TO</span>
            <input 
              type="date" 
              name="date_to"
              value={filters.date_to}
              onChange={handleChange}
              style={{ flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: 'white', padding: '8px 10px', fontSize: '12px', outline: 'none', colorScheme: 'dark' }} 
            />
          </div>
        </div>
      </div>

      {/* Fire Types */}
      <div>
        <h4 style={{ fontSize: '13px', color: '#fff', fontWeight: 500, letterSpacing: '0.5px', marginBottom: '12px' }}>Classification Focus</h4>
        <select 
          name="ml_label"
          value={filters.ml_label}
          onChange={handleChange}
          style={{ width: '100%', colorScheme: 'dark', backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: 'white', padding: '10px 14px', outline: 'none', fontSize: '13px' }}
        >
          <option value="" style={{background: '#15171e'}}>All Classifications</option>
          <option value="Industrial Fire" style={{background: '#15171e'}}>Industrial Fire</option>
          <option value="Forest Fire" style={{background: '#15171e'}}>Forest Fire</option>
          <option value="Gas Flare" style={{background: '#15171e'}}>Gas Flare</option>
          <option value="Agricultural Burn" style={{background: '#15171e'}}>Agricultural Burn</option>
          <option value="Mining/Thermal" style={{background: '#15171e'}}>Mining/Thermal</option>
        </select>
      </div>

      {/* Confidence Slider */}
      <div>
        <h4 style={{ fontSize: '13px', color: '#fff', fontWeight: 500, letterSpacing: '0.5px', marginBottom: '12px' }}>Min Confidence</h4>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
          <span>0%</span>
          <span style={{ color: 'white', fontWeight: 600 }}>{filters.min_confidence}%</span>
        </div>
        <input 
          type="range" 
          name="min_confidence"
          min="0" 
          max="100" 
          value={filters.min_confidence} 
          onChange={handleChange}
          className="custom-slider" 
          style={{ width: '100%', accentColor: '#1e90ff' }} 
        />
      </div>

      {/* Region */}
      <div>
        <h4 style={{ fontSize: '13px', color: '#fff', fontWeight: 500, letterSpacing: '0.5px', marginBottom: '12px' }}>Geographic Region</h4>
        <select 
          name="region"
          value={filters.region || 'global'}
          onChange={handleChange}
          style={{ 
          width: '100%', 
          padding: '10px 12px', 
          backgroundColor: 'rgba(255,255,255,0.05)',
          border: '1px solid rgba(255,255,255,0.1)',
          color: 'white',
          borderRadius: '8px',
          fontSize: '13px',
          outline: 'none',
          cursor: 'pointer',
          colorScheme: 'dark',
          transition: 'border-color 0.2s'
        }}
        onFocus={(e) => e.target.style.borderColor = '#00a8ff'}
        onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
        >
          <option value="global" style={{background: '#15171e'}}>Global View</option>
          <option value="north_america" style={{background: '#15171e'}}>North America (NORAD)</option>
          <option value="europe" style={{background: '#15171e'}}>Europe & Middle East</option>
          <option value="asia" style={{background: '#15171e'}}>Asia Pacific (INDOPACOM)</option>
          <option value="south_america" style={{background: '#15171e'}}>South America</option>
          <option value="africa" style={{background: '#15171e'}}>Africa Command (AFRICOM)</option>
        </select>
      </div>

    </div>
  );
};

export default FilterPanel;
