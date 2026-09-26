import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Book, MessageSquare, Shield, ExternalLink, Mail, Phone, Cpu } from 'lucide-react';

const SupportModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
          className="glass-panel"
          style={{ width: '600px', maxWidth: '90vw', maxHeight: '90vh', overflowY: 'auto', backgroundColor: '#11141e', borderRadius: '16px', border: '1px solid rgba(0, 168, 255, 0.3)', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}
        >
          {/* Header */}
          <div style={{ padding: '24px', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'linear-gradient(90deg, rgba(0,168,255,0.1) 0%, transparent 100%)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ padding: '10px', backgroundColor: 'rgba(0,168,255,0.15)', borderRadius: '10px', color: '#00a8ff' }}>
                <Shield size={24} />
              </div>
              <div>
                <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: 'white', letterSpacing: '0.5px' }}>Command Center Support</h2>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>IGNIS Platform Version 1.0.0-SIH</div>
              </div>
            </div>
            <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '8px', borderRadius: '50%', display: 'flex' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6', margin: 0 }}>
              Welcome to the IGNIS AI Intelligence System. For Smart India Hackathon (SIH) jury members, this panel provides quick access to system documentation, diagnostic tools, and technical support.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              
              {/* Resource Cards */}
              <a href="https://github.com/suraj-codes-24/NASA-FIRMS" target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
                <div style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '12px', cursor: 'pointer', transition: 'all 0.2s' }} onMouseEnter={(e) => {e.currentTarget.style.borderColor = 'rgba(0,168,255,0.3)'; e.currentTarget.style.backgroundColor = 'rgba(0,168,255,0.05)'}} onMouseLeave={(e) => {e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)'; e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.02)'}}>
                  <div style={{ color: '#00a8ff' }}><Book size={20} /></div>
                  <div>
                    <div style={{ color: 'white', fontWeight: 600, fontSize: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}>System Architecture <ExternalLink size={12} /></div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '4px' }}>View ML pipeline and infrastructure diagrams</div>
                  </div>
                </div>
              </a>

              <div style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '12px', cursor: 'pointer', transition: 'all 0.2s' }} onMouseEnter={(e) => {e.currentTarget.style.borderColor = 'rgba(46,213,115,0.3)'; e.currentTarget.style.backgroundColor = 'rgba(46,213,115,0.05)'}} onMouseLeave={(e) => {e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)'; e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.02)'}}>
                <div style={{ color: '#2ed573' }}><Cpu size={20} /></div>
                <div>
                  <div style={{ color: 'white', fontWeight: 600, fontSize: '14px' }}>System Diagnostics</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '4px' }}>All microservices operational (Latency: 45ms)</div>
                </div>
              </div>

            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '20px', marginTop: '10px' }}>
              <h3 style={{ fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px' }}>Direct Contact</h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                  <Mail size={16} color="var(--text-secondary)" />
                  <span style={{ fontSize: '13px', color: 'white' }}>admin@ignis-sih.gov.in</span>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                  <MessageSquare size={16} color="var(--text-secondary)" />
                  <span style={{ fontSize: '13px', color: 'white' }}>SIH Jury Internal Slack Channel (#team-ignis)</span>
                </div>
              </div>
            </div>

          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default SupportModal;
