import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Flame, ShieldAlert, Activity } from 'lucide-react';

const SplashScreen = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('INITIALIZING IGNIS_OS...');
  const [isVisible, setIsVisible] = useState(true);
  const [hexCodes, setHexCodes] = useState([]);

  // Generate random hex codes for the background HUD effect
  useEffect(() => {
    const codes = Array.from({ length: 20 }).map(() => ({
      id: Math.random().toString(36).substr(2, 9),
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 2,
      duration: Math.random() * 3 + 2,
      text: `0x${Math.floor(Math.random() * 16777215).toString(16).toUpperCase()}`
    }));
    setHexCodes(codes);
  }, []);

  useEffect(() => {
    const sequence = [
      { p: 15, s: 'ESTABLISHING SECURE UPLINK...', t: 300 },
      { p: 35, s: 'SYNCING MODIS & VIIRS TELEMETRY...', t: 800 },
      { p: 60, s: 'CALIBRATING THERMAL SENSORS...', t: 1300 },
      { p: 85, s: 'EXECUTING NEURAL NETWORKS...', t: 1800 },
      { p: 100, s: 'SYSTEM ONLINE', t: 2400 }
    ];

    const timeouts = [];

    sequence.forEach((step) => {
      const to = setTimeout(() => {
        setProgress(step.p);
        setStatus(step.s);
      }, step.t);
      timeouts.push(to);
    });

    const finishTimeout = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => {
        onComplete();
      }, 800); // Wait for exit animation
    }, 2800);

    timeouts.push(finishTimeout);

    return () => timeouts.forEach(clearTimeout);
  }, [onComplete]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 1.1, filter: 'blur(10px)' }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'color-mix(in srgb, var(--bg-main) 70%, transparent)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            zIndex: 99999,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'monospace',
            overflow: 'hidden'
          }}
        >
          {/* Background HUD Grid */}
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.05, backgroundImage: 'linear-gradient(var(--text-primary) 1px, transparent 1px), linear-gradient(90deg, var(--text-primary) 1px, transparent 1px)', backgroundSize: '40px 40px', zIndex: 0 }}></div>
          
          {/* Background Hex Codes */}
          {hexCodes.map((code) => (
            <motion.div
              key={code.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: [0, 0.5, 0], y: -20 }}
              transition={{ duration: code.duration, delay: code.delay, repeat: Infinity }}
              style={{
                position: 'absolute',
                left: `${code.x}%`,
                top: `${code.y}%`,
                color: 'var(--color-facility)',
                fontSize: '10px',
                fontWeight: 600,
                zIndex: 1,
                opacity: 0.2
              }}
            >
              {code.text}
            </motion.div>
          ))}

          {/* Central Radar Pulse */}
          <motion.div
            animate={{ scale: [1, 2, 3], opacity: [0.5, 0, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }}
            style={{
              position: 'absolute',
              width: '100px', height: '100px',
              borderRadius: '50%',
              border: '1px solid var(--color-facility)',
              zIndex: 1
            }}
          />

          <div style={{ zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <motion.div 
              initial={{ scale: 0.5, opacity: 0, rotate: -45 }}
              animate={{ scale: 1, opacity: 1, rotate: 0 }}
              transition={{ duration: 0.7, type: 'spring', bounce: 0.5 }}
              style={{
                width: '72px', height: '72px',
                background: 'linear-gradient(135deg, var(--color-facility) 0%, #9b51e0 100%)',
                borderRadius: '18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '32px',
                boxShadow: '0 0 40px rgba(0, 168, 255, 0.4), inset 0 0 20px rgba(255,255,255,0.2)',
                position: 'relative'
              }}
            >
              <Flame size={36} color="#ffffff" strokeWidth={2.5} />
            </motion.div>

            <motion.h1 
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              style={{ fontSize: '36px', letterSpacing: '8px', margin: '0 0 12px 0', color: 'var(--text-primary)', fontWeight: 700 }}
            >
              IGNIS
            </motion.h1>
            
            <motion.div 
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              style={{ fontSize: '13px', letterSpacing: '3px', color: 'var(--text-secondary)', marginBottom: '48px', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}
            >
              <ShieldAlert size={14} /> INDUSTRIAL FIRE SURVEILLANCE
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: '320px' }}
              transition={{ duration: 0.5, delay: 0.5 }}
              style={{ height: '3px', backgroundColor: 'var(--border-light)', overflow: 'hidden', position: 'relative', borderRadius: '4px' }}
            >
              <motion.div 
                initial={{ width: '0%' }}
                animate={{ width: `${progress}%` }}
                transition={{ ease: "easeOut", duration: 0.4 }}
                style={{ position: 'absolute', top: 0, left: 0, height: '100%', backgroundColor: 'var(--color-facility)', boxShadow: '0 0 15px var(--color-facility)' }}
              />
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              style={{ marginTop: '20px', display: 'flex', justifyContent: 'space-between', width: '320px' }}
            >
              <div style={{ fontSize: '11px', letterSpacing: '1px', color: 'var(--color-facility)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Activity size={12} className={progress < 100 ? "pulse-ring" : ""} /> {status}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
                {progress}%
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SplashScreen;
