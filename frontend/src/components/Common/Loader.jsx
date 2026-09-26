import React from 'react';
import { motion } from 'framer-motion';

const Loader = ({ size = 40, color = '#e74c3c', text = 'Loading...' }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '12px',
      padding: '24px',
    }}
  >
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      style={{
        width: size,
        height: size,
        border: `3px solid rgba(255,255,255,0.1)`,
        borderTop: `3px solid ${color}`,
        borderRadius: '50%',
      }}
    />
    {text && (
      <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 500 }}>
        {text}
      </span>
    )}
  </motion.div>
);

export default Loader;
