import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Flame, CheckCircle, Navigation, Map as MapIcon, Clock, ShieldCheck, X } from 'lucide-react';

const ClassificationDetails = ({ hotspot, onClose }) => {
  if (!hotspot) return null;

  const getThemeColor = (label) => {
    if (label === 'Industrial Fire') return '#ef4444';
    if (label === 'Forest Fire') return '#f97316';
    if (label === 'Gas Flare') return '#eab308';
    if (label === 'Agricultural Burn') return '#10b981';
    if (label === 'Mining/Thermal') return '#3b82f6';
    return '#9ca3af';
  };

  const themeColor = getThemeColor(hotspot.ml_label);
  const isAlert = hotspot.ml_label === 'Industrial Fire';

  const [address, setAddress] = useState('Fetching location...');

  useEffect(() => {
    if (!hotspot) return;
    
    let isMounted = true;
    const fetchAddress = async () => {
      setAddress('Fetching location...');
      try {
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${hotspot.latitude}&lon=${hotspot.longitude}&accept-language=en`);
        const data = await res.json();
        
        if (isMounted) {
          if (data && data.address) {
            const loc = data.address;
            const detail = loc.city || loc.town || loc.village || loc.suburb || loc.neighbourhood || loc.county || loc.state_district || loc.municipality || '';
            const state = loc.state || loc.region || '';
            const country = loc.country || '';
            
            const parts = [detail, state, country].filter(Boolean);
            // Use Set to remove duplicates in case state_district and state are the same
            const uniqueParts = [...new Set(parts)];
            
            if (uniqueParts.length > 0) {
              setAddress(uniqueParts.join(', '));
            } else {
              setAddress('Remote Location');
            }
          } else {
            setAddress('Remote Location');
          }
        }
      } catch (err) {
        console.error('Error fetching address:', err);
        if (isMounted) setAddress('Location unavailable');
      }
    };

    // Add a slight delay to respect rate limits if many hotspots are clicked quickly
    const timeout = setTimeout(fetchAddress, 300);
    return () => {
      isMounted = false;
      clearTimeout(timeout);
    };
  }, [hotspot?.latitude, hotspot?.longitude]);

  return (
    <AnimatePresence>
      <motion.div
        className="glass-panel"
        initial={{ x: 400, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 400, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        style={{ 
          width: '380px', 
          position: 'absolute', 
          top: '20px', 
          right: '20px', 
          zIndex: 1000, 
          display: 'flex', 
          flexDirection: 'column', 
          backgroundColor: 'var(--bg-card)',
          borderTop: `3px solid ${themeColor}`,
          boxShadow: `0 10px 40px rgba(0,0,0,0.3), 0 0 20px ${themeColor}15`, 
          overflow: 'hidden' 
        }}
      >
        {/* Header with Gradient */}
        <div style={{ 
          background: `linear-gradient(90deg, ${themeColor}22 0%, transparent 100%)`, 
          padding: '20px', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start' 
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: themeColor, boxShadow: `0 0 8px ${themeColor}` }}></div>
              <span style={{ fontWeight: 600, fontSize: '10px', letterSpacing: '1.5px', color: 'var(--text-secondary)' }}>TARGET PROFILE</span>
            </div>
            <h2 style={{ fontSize: '22px', margin: 0, fontWeight: '700', color: 'var(--text-primary)', fontFamily: 'monospace', letterSpacing: '-0.5px' }}>
              SIG-{hotspot.id || 'UNK'}
            </h2>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: '1px solid var(--border-color)', borderRadius: '50%', color: 'var(--text-primary)', cursor: 'pointer', padding: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'background 0.2s' }}>
            <X size={16} />
          </button>
        </div>
        
        {/* Content Body */}
        <div style={{ padding: '0 20px 20px 20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Main Classification Pill */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-main)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-secondary)', fontSize: '13px' }}>
              <Flame size={16} color={themeColor} /> Classification
            </div>
            <div style={{ background: `${themeColor}15`, color: themeColor, padding: '4px 10px', borderRadius: '4px', fontSize: '12px', fontWeight: 600, border: `1px solid ${themeColor}30` }}>
              {hotspot.ml_label ? hotspot.ml_label.toUpperCase() : 'UNCLASSIFIED'}
            </div>
          </div>

          {/* Grid Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {/* FRP */}
            <div style={{ background: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Flame size={12} /> RADIATIVE POWER
              </div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                {hotspot.frp} <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>MW</span>
              </div>
            </div>

            {/* Persistence */}
            <div style={{ background: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={12} /> PERSISTENCE
              </div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                {hotspot.persistence_hours || 0} <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>HRS</span>
              </div>
            </div>
          </div>

          {/* AI Confidence Bar */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
              <div style={{ color: 'var(--text-secondary)' }}>AI Confidence Score</div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontFamily: 'monospace' }}>{hotspot.confidence}%</div>
            </div>
            <div style={{ width: '100%', height: '6px', backgroundColor: 'var(--bg-main)', borderRadius: '3px', overflow: 'hidden', border: '1px solid var(--border-light)' }}>
              <div style={{ 
                width: `${hotspot.confidence}%`, 
                height: '100%', 
                background: `linear-gradient(90deg, ${themeColor}aa 0%, ${themeColor} 100%)`, 
                borderRadius: '3px',
                boxShadow: `0 0 10px ${themeColor}80`
              }}></div>
            </div>
          </div>

          {/* Coordinates Terminal Readout */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <MapIcon size={12} /> TELEMETRY & LOCATION
            </div>
            <div style={{ 
              background: 'var(--bg-main)', 
              border: '1px solid var(--border-light)', 
              padding: '12px', 
              borderRadius: '6px', 
              display: 'flex', 
              flexDirection: 'column',
              gap: '8px'
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                fontFamily: 'monospace',
                fontSize: '13px',
                color: themeColor
              }}>
                <span>LAT: {hotspot.latitude.toFixed(5)}</span>
                <span>LON: {hotspot.longitude.toFixed(5)}</span>
                <Navigation size={14} style={{ opacity: 0.5 }} />
              </div>
              
              {/* Address Readout */}
              <div style={{ 
                borderTop: '1px dashed var(--border-light)', 
                paddingTop: '8px', 
                fontSize: '12px', 
                color: 'var(--text-secondary)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px'
              }}>
                <div style={{ marginTop: '2px', color: themeColor }}>
                  <MapIcon size={12} />
                </div>
                <div style={{ lineHeight: '1.4' }}>
                  {address}
                </div>
              </div>
            </div>
          </div>

          {/* Status Footer */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', padding: '12px', background: `${themeColor}15`, borderRadius: '6px', border: `1px solid ${themeColor}30` }}>
            <ShieldCheck size={16} color={themeColor} />
            <span style={{ fontSize: '12px', fontWeight: 600, color: themeColor }}>
              SYSTEM STATUS: {isAlert ? 'CRITICAL ALERT LOGGED' : 'ROUTINE MONITORING'}
            </span>
          </div>

        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ClassificationDetails;
