import React, { useState, useEffect } from 'react';
import { Shield, Lock, Eye, EyeOff, Activity, Globe, Cpu, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

import { API_BASE } from '../config';

export default function LoginPage() {
  const [username, setUsername] = useState('admin@ignis.gov');
  const [password, setPassword] = useState('admin123');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [fullName, setFullName] = useState('');
  
  // Tactical typing effect for terminal
  const [terminalText, setTerminalText] = useState('');
  const fullText = "CONNECTION SECURED.\nSATELLITE UPLINK: STABLE.\nNEURAL ENGINE: ONLINE.\nAWAITING AUTHORIZATION...";
  
  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setTerminalText(fullText.substring(0, i));
      i++;
      if (i > fullText.length) clearInterval(interval);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      if (isRegister) {
        await axios.post(`${API_BASE}/auth/register`, { 
          email: username, 
          password, 
          full_name: fullName 
        });
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
        const res = await axios.post(`${API_BASE}/auth/login`, params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        localStorage.setItem('ignis_token', res.data.access_token);
        localStorage.setItem('ignis_user', JSON.stringify(res.data.user));
        window.location.href = '/';
      } else {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
        const res = await axios.post(`${API_BASE}/auth/login`, params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        localStorage.setItem('ignis_token', res.data.access_token);
        localStorage.setItem('ignis_user', JSON.stringify(res.data.user));
        window.location.href = '/';
      }
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Authentication failed. Please verify your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', background: '#090a0f', color: '#fff', fontFamily: '"Inter", sans-serif'
    }}>
      {/* LEFT PANEL: Tactical Branding */}
      <div style={{
        flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', padding: '4rem',
        borderRight: '1px solid rgba(255,255,255,0.05)', background: 'radial-gradient(circle at center, #11131a 0%, #090a0f 100%)',
        overflow: 'hidden'
      }}>
        {/* Subtle Grid Background */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.03, pointerEvents: 'none',
          backgroundImage: 'linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)',
          backgroundSize: '40px 40px'
        }}></div>

        <div style={{ zIndex: 1, display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: 'auto' }}>
          <div style={{ padding: '10px', background: 'rgba(231, 76, 60, 0.1)', borderRadius: '12px', border: '1px solid rgba(231, 76, 60, 0.2)' }}>
            <Shield size={28} color="#e74c3c" />
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.8rem', letterSpacing: '2px', fontWeight: 800 }}>IGNIS</h1>
            <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', letterSpacing: '1px', textTransform: 'uppercase' }}>
              Strategic Threat Detection
            </div>
          </div>
        </div>

        <div style={{ zIndex: 1, marginTop: 'auto', marginBottom: 'auto', maxWidth: '400px' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 300, lineHeight: 1.2, marginBottom: '1.5rem' }}>
            Advanced <br/>
            <strong style={{ fontWeight: 700, color: '#e74c3c' }}>Geospatial Intelligence.</strong>
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, fontSize: '0.95rem' }}>
            Authorised personnel only. IGNIS utilises real-time VIIRS & MODIS satellite telemetry combined with Random Forest ML inference to autonomously detect and classify critical industrial thermal anomalies.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '3rem' }}>
            <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderLeft: '2px solid #e74c3c', borderRadius: '0 8px 8px 0' }}>
              <Globe size={18} color="#e74c3c" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase' }}>Coverage</div>
              <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>Global (NASA)</div>
            </div>
            <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderLeft: '2px solid #3498db', borderRadius: '0 8px 8px 0' }}>
              <Cpu size={18} color="#3498db" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase' }}>Engine Status</div>
              <div style={{ fontWeight: 600, fontSize: '1.1rem', color: '#2ecc71' }}>ONLINE</div>
            </div>
          </div>
        </div>

        <div style={{ zIndex: 1, marginTop: 'auto', fontFamily: 'monospace', color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem', whiteSpace: 'pre-line', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
          {terminalText}
          <span className="blinking-cursor">_</span>
        </div>
      </div>

      {/* RIGHT PANEL: Auth Form */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative'
      }}>
        <div style={{ width: '400px', padding: '2rem' }}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <h2 style={{ fontSize: '1.8rem', marginBottom: '0.5rem', fontWeight: 600 }}>
              {isRegister ? 'Clearance Request' : 'System Authentication'}
            </h2>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.9rem', marginBottom: '2.5rem' }}>
              {isRegister ? 'Register for system access.' : 'Enter your credentials to access the secure uplink.'}
            </p>

            <form onSubmit={handleAuth}>
              {isRegister && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'rgba(255,255,255,0.6)', display: 'block', marginBottom: 8 }}>
                    Full Name
                  </label>
                  <input
                    type="text" value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Operative Name" required
                    style={{
                      width: '100%', padding: '0.85rem 1rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)',
                      background: 'rgba(0,0,0,0.2)', color: '#fff', fontSize: '1rem', outline: 'none', transition: 'border 0.3s'
                    }}
                    onFocus={e => e.target.style.borderColor = '#e74c3c'}
                    onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                </div>
              )}

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'rgba(255,255,255,0.6)', display: 'block', marginBottom: 8 }}>
                  Identification (Email)
                </label>
                <input
                  type="email" value={username} onChange={e => setUsername(e.target.value)} placeholder="agent@ignis.gov" required
                  style={{
                    width: '100%', padding: '0.85rem 1rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)',
                    background: 'rgba(0,0,0,0.2)', color: '#fff', fontSize: '1rem', outline: 'none', transition: 'border 0.3s'
                  }}
                  onFocus={e => e.target.style.borderColor = '#e74c3c'}
                  onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'rgba(255,255,255,0.6)', display: 'block', marginBottom: 8 }}>
                  Passcode
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required
                    style={{
                      width: '100%', padding: '0.85rem 2.5rem 0.85rem 1rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)',
                      background: 'rgba(0,0,0,0.2)', color: '#fff', fontSize: '1rem', outline: 'none', transition: 'border 0.3s'
                    }}
                    onFocus={e => e.target.style.borderColor = '#e74c3c'}
                    onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                  <button type="button" onClick={() => setShowPw(!showPw)} style={{
                    position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)', cursor: 'pointer', padding: 0
                  }}>
                    {showPw ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {error && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} style={{ marginBottom: '1.5rem' }}>
                  <div style={{ padding: '0.75rem', borderRadius: '4px', background: 'rgba(231, 76, 60, 0.1)', borderLeft: '3px solid #e74c3c', color: '#e74c3c', fontSize: '0.85rem' }}>
                    {error}
                  </div>
                </motion.div>
              )}

              <button type="submit" disabled={loading} style={{
                width: '100%', padding: '1rem', borderRadius: '4px', border: 'none', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px',
                fontSize: '0.9rem', cursor: loading ? 'wait' : 'pointer', background: '#e74c3c', color: '#fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, transition: 'background 0.3s'
              }}
              onMouseOver={e => !loading && (e.target.style.background = '#c0392b')}
              onMouseOut={e => !loading && (e.target.style.background = '#e74c3c')}
              >
                {loading ? <Activity size={18} className="spin" /> : <Lock size={18} />} 
                {loading ? 'VERIFYING...' : (isRegister ? 'REQUEST CLEARANCE' : 'AUTHORISE')}
              </button>
              
              <div style={{ textAlign: 'center', marginTop: '1.5rem', color: 'rgba(255,255,255,0.3)', fontSize: '0.8rem' }}>
                <span style={{ display: 'inline-block', padding: '4px 8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                  <strong>SIH Jury Access:</strong> admin@ignis.gov / admin123
                </span>
              </div>
            </form>

            <div style={{ textAlign: 'center', marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <button 
                type="button" 
                onClick={() => { setIsRegister(!isRegister); setError(''); }}
                style={{ 
                  background: 'none', border: 'none', color: 'rgba(255,255,255,0.5)', fontSize: '0.85rem',
                  cursor: 'pointer', transition: 'color 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'
                }}
                onMouseOver={e => e.target.style.color = '#fff'}
                onMouseOut={e => e.target.style.color = 'rgba(255,255,255,0.5)'}
              >
                {isRegister ? "Return to Authorization" : "Request System Clearance"} <ChevronRight size={14} style={{ marginLeft: 4 }} />
              </button>
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* Blinking cursor style */}
      <style>{`
        .blinking-cursor {
          animation: blink 1s step-end infinite;
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        .spin {
          animation: spin 2s linear infinite;
        }
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
