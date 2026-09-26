import { API_BASE } from '../config';
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Bell, Moon, Globe, Shield, Database, Key, CheckCircle2, X } from 'lucide-react';
import { updateSettings, changePassword, logout } from '../api';
import { useSettings } from '../contexts/SettingsContext';

const pageTransition = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 }
};

const SettingCard = ({ icon, title, description, children, highlightColor = '#e74c3c' }) => (
  <div className="glass-panel" style={{
    padding: '24px',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '20px',
    borderRadius: '16px',
    border: '1px solid rgba(255,255,255,0.05)',
    background: 'linear-gradient(145deg, rgba(30,33,43,0.6) 0%, rgba(20,22,30,0.8) 100%)',
    boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
  }}>
    <div style={{
      backgroundColor: `${highlightColor}15`,
      padding: '12px',
      borderRadius: '12px',
      color: highlightColor,
      flexShrink: 0,
      border: `1px solid ${highlightColor}30`
    }}>
      {icon}
    </div>
    <div style={{ flex: 1 }}>
      <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: 'white', letterSpacing: '0.3px' }}>{title}</h3>
      <p style={{ margin: '6px 0 16px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>{description}</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {children}
      </div>
    </div>
  </div>
);

const Toggle = ({ label, storageKey, defaultChecked = false, settingsDict, onChange }) => {
  const isChecked = settingsDict[storageKey] !== undefined ? settingsDict[storageKey] === 'true' : defaultChecked;

  const toggle = () => {
    onChange(storageKey, (!isChecked).toString());
  };

  return (
    <label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={toggle}>
      <div 
        className="toggle-track"
        style={{
        width: '42px', height: '22px', borderRadius: '11px', position: 'relative',
        backgroundColor: isChecked ? '#00a8ff' : 'rgba(255,255,255,0.1)',
        transition: 'background 0.3s ease',
        flexShrink: 0,
        boxShadow: isChecked ? '0 0 10px rgba(0, 168, 255, 0.4)' : 'none'
      }}>
        <div 
          className="toggle-knob"
          style={{
          position: 'absolute', top: '2px', left: isChecked ? '22px' : '2px',
          width: '18px', height: '18px', borderRadius: '50%',
          backgroundColor: 'white',
          transition: 'left 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
        }} />
      </div>
      <span style={{ fontSize: '14px', color: isChecked ? 'white' : 'var(--text-secondary)', transition: 'color 0.2s' }}>{label}</span>
    </label>
  );
};

const SettingsPage = () => {
  const { settings, refreshSettings, loading } = useSettings();
  const [localSettings, setLocalSettings] = useState(settings);
  const [keySaved, setKeySaved] = useState(false);
  const [intervalSaved, setIntervalSaved] = useState(false);
  
  // Password state
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [passwordStatus, setPasswordStatus] = useState(''); // '', 'success', 'error'

  const handleChange = async (key, value) => {
    setLocalSettings(prev => ({ ...prev, [key]: value }));
    try {
      await updateSettings({ [key]: value });
      await refreshSettings();
    } catch (e) {
      console.error('Failed to sync setting:', e);
    }
  };

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleSaveKey = async () => {
    await handleChange('firms_api_key', localSettings['firms_api_key'] || '');
    setKeySaved(true);
    setTimeout(() => setKeySaved(false), 2000);
  };

  const handleIntervalChange = async (e) => {
    const val = e.target.value;
    await handleChange('settings_ingestion', val);
    setIntervalSaved(true);
    setTimeout(() => setIntervalSaved(false), 2000);
  };

  const handleChangePasswordSubmit = async () => {
    if (!newPassword) return;
    try {
      await changePassword(newPassword);
      setPasswordStatus('success');
      setNewPassword('');
      setTimeout(() => {
        setShowPasswordChange(false);
        setPasswordStatus('');
      }, 2000);
    } catch (err) {
      setPasswordStatus('error');
    }
  };

  const handleSignOut = async () => {
    try {
      await logout();
    } catch (e) {
      console.error(e);
    }
    localStorage.removeItem('ignis_token');
    localStorage.removeItem('ignis_user');
    window.location.href = '/login';
  };

  if (loading) {
    return <div style={{ padding: '40px', color: 'white' }}>Loading settings...</div>;
  }

  const apiKey = localSettings['firms_api_key'] || '';
  const webhookUrl = localSettings['settings_webhook_url'] || '';
  const ingestionInterval = localSettings['settings_ingestion'] || '3';

  return (
    <motion.div {...pageTransition} style={{
      height: '100%', width: '100%', padding: '32px 40px', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto'
    }}>
      <div style={{ marginBottom: '16px' }}>
        <p style={{ margin: 0, fontSize: '15px', color: 'var(--text-secondary)' }}>
          Configure your IGNIS dashboard preferences, API integrations, and alert tolerances.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        
        {/* API Key Setting */}
        <SettingCard icon={<Key size={22} />} title="NASA FIRMS Integration" description="Authenticate with NASA FIRMS to fetch real-time global anomaly and satellite fire data." highlightColor="#3742fa">
          <div style={{ display: 'flex', gap: '12px' }}>
            <input 
              type="password"
              value={apiKey}
              onChange={(e) => setLocalSettings(p => ({...p, 'firms_api_key': e.target.value}))}
              placeholder="Enter API Key (e.g. 1a2b3c...)"
              style={{
                flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', 
                backgroundColor: 'rgba(0,0,0,0.3)', color: 'white', outline: 'none', fontSize: '14px', transition: 'border 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#3742fa'} onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
            />
            <button 
              onClick={handleSaveKey}
              style={{
                padding: '10px 20px', borderRadius: '8px', border: 'none', background: keySaved ? '#2ed573' : 'linear-gradient(135deg, #3742fa, #5352ed)',
                color: 'white', fontWeight: 600, fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', transition: 'background 0.3s'
              }}
            >
              {keySaved ? <><CheckCircle2 size={16} /> Saved</> : 'Save Key'}
            </button>
          </div>
        </SettingCard>

        {/* Notifications */}
        <SettingCard icon={<Bell size={22} />} title="Notification Preferences" description="Control how and when you receive alerts about critical fire events." highlightColor="#ff9f43">
          <Toggle label="Push notifications for Industrial Fires" storageKey="settings_notif_ind" defaultChecked={true} settingsDict={localSettings} onChange={handleChange} />
          <Toggle label="Push notifications for Gas Flares" storageKey="settings_notif_gas" defaultChecked={false} settingsDict={localSettings} onChange={handleChange} />
          <Toggle label="Email digest (daily summary)" storageKey="settings_notif_email" defaultChecked={false} settingsDict={localSettings} onChange={handleChange} />
          <Toggle label="Sound alerts for CRITICAL severity" storageKey="settings_notif_sound" defaultChecked={true} settingsDict={localSettings} onChange={handleChange} />
          
          <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid var(--border-light)' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>External Webhook Alerts (Slack/Discord)</h4>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input 
                type="text"
                value={webhookUrl}
                onChange={(e) => setLocalSettings(p => ({...p, 'settings_webhook_url': e.target.value}))}
                onBlur={() => handleChange('settings_webhook_url', webhookUrl)}
                placeholder="https://hooks.slack.com/services/..."
                style={{
                  flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--border-color)', 
                  backgroundColor: 'var(--bg-main)', color: 'var(--text-primary)', outline: 'none', fontSize: '13px'
                }}
              />
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
              If provided, CRITICAL industrial fires will trigger an instant POST payload to this URL.
            </p>
          </div>
        </SettingCard>

        {/* Map Preferences */}
        <SettingCard icon={<Globe size={22} />} title="Map Visualization" description="Customize the default map view, clustering, and layer settings." highlightColor="#10b981">
          <Toggle label="Show industrial facility buffers by default" storageKey="settings_map_buffers" defaultChecked={true} settingsDict={localSettings} onChange={handleChange} />
          <Toggle label="Show heatmap layer by default" storageKey="settings_map_heatmap" defaultChecked={false} settingsDict={localSettings} onChange={handleChange} />
          <Toggle label="Cluster markers at low zoom levels" storageKey="settings_map_cluster" defaultChecked={true} settingsDict={localSettings} onChange={handleChange} />
        </SettingCard>

        {/* Data Ingestion */}
        <SettingCard icon={<Database size={22} />} title="Data Ingestion" description="Configure automatic FIRMS data fetching schedule." highlightColor="#10ac84">
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <label style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Ingestion interval:</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <select 
                value={ingestionInterval}
                onChange={handleIntervalChange}
                style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-primary)', fontSize: '14px', colorScheme: 'dark', outline: 'none', cursor: 'pointer' }}
              >
                <option value="0.16666">Every 10 minutes (Auto-Update)</option>
                <option value="1">Every 1 hour</option>
                <option value="3">Every 3 hours</option>
                <option value="6">Every 6 hours</option>
                <option value="12">Every 12 hours</option>
              </select>
              <AnimatePresence>
                {intervalSaved && (
                  <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}>
                    <CheckCircle2 size={18} color="#2ed573" />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
          
          <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid var(--border-light)' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>Manual Override</h4>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
              Bypass the scheduler and immediately pull the latest thermal signatures from NASA FIRMS. This will also trigger the ML pipeline to classify and analyze the new data.
            </p>
            <button 
              onClick={async (e) => {
                const btn = e.currentTarget;
                const originalText = btn.innerHTML;
                btn.innerHTML = 'Triggering...';
                try {
                  await fetch(`${API_BASE.replace('/api/v1', '')}/hotspots/trigger-ingestion`, { method: 'POST' });
                  btn.innerHTML = 'Ingestion Triggered!';
                  btn.style.background = '#2ed573';
                  setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = 'linear-gradient(135deg, #3742fa, #5352ed)';
                  }, 3000);
                } catch(err) {
                  btn.innerHTML = 'Error Triggering';
                  btn.style.background = '#ef4444';
                  setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = 'linear-gradient(135deg, #3742fa, #5352ed)';
                  }, 3000);
                }
              }}
              style={{
                padding: '10px 16px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #3742fa, #5352ed)',
                color: 'white', fontWeight: 600, fontSize: '13px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px'
              }}
            >
              <Database size={14} /> FORCE IMMEDIATE SYNC
            </button>
          </div>
        </SettingCard>

        {/* Appearance */}
        <SettingCard icon={<Moon size={22} />} title="Appearance" description="Theme and display customization." highlightColor="#3b82f6">
          <Toggle label="Dark mode (default)" storageKey="settings_theme_dark" defaultChecked={true} settingsDict={localSettings} onChange={handleChange} />
        </SettingCard>

        {/* Account & Security */}
        <SettingCard icon={<Shield size={22} />} title="Account & Security" description="Manage your account settings and active sessions." highlightColor="#ee5253">
          <AnimatePresence mode="wait">
            {!showPasswordChange ? (
              <motion.div key="buttons" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ display: 'flex', gap: '12px' }}>
                <button 
                  className="btn-outline"
                  onClick={() => setShowPasswordChange(true)}
                  style={{ padding: '10px 18px', borderRadius: '8px', border: '1px solid var(--border-light)', backgroundColor: 'var(--bg-main)', color: 'var(--text-primary)', fontSize: '14px', cursor: 'pointer', fontWeight: 500, transition: 'background 0.2s' }} 
                  onMouseEnter={(e)=>e.target.style.backgroundColor='rgba(255,255,255,0.1)'} onMouseLeave={(e)=>e.target.style.backgroundColor='rgba(255,255,255,0.05)'}>
                  Change Password
                </button>
                <button 
                  className="btn-danger"
                  onClick={handleSignOut}
                  style={{ padding: '10px 18px', borderRadius: '8px', border: '1px solid rgba(238, 82, 83, 0.3)', backgroundColor: 'rgba(238, 82, 83, 0.1)', color: '#ee5253', fontSize: '14px', cursor: 'pointer', fontWeight: 500, transition: 'background 0.2s' }} 
                  onMouseEnter={(e)=>e.target.style.backgroundColor='rgba(238, 82, 83, 0.2)'} onMouseLeave={(e)=>e.target.style.backgroundColor='rgba(238, 82, 83, 0.1)'}>
                  Sign Out
                </button>
              </motion.div>
            ) : (
              <motion.div key="input" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input 
                    type="password" 
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter new password"
                    style={{ flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-primary)', outline: 'none', fontSize: '14px' }}
                  />
                  <button 
                    onClick={handleChangePasswordSubmit}
                    disabled={!newPassword || passwordStatus === 'success'}
                    style={{ padding: '10px 18px', borderRadius: '8px', border: 'none', backgroundColor: passwordStatus === 'success' ? '#2ed573' : '#3742fa', color: 'white', fontSize: '14px', cursor: 'pointer', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px' }}>
                    {passwordStatus === 'success' ? <><CheckCircle2 size={16}/> Updated</> : 'Confirm'}
                  </button>
                  <button 
                    onClick={() => { setShowPasswordChange(false); setNewPassword(''); setPasswordStatus(''); }}
                    style={{ padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'transparent', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <X size={18} />
                  </button>
                </div>
                {passwordStatus === 'error' && <span style={{ color: '#ee5253', fontSize: '13px' }}>Failed to update password.</span>}
              </motion.div>
            )}
          </AnimatePresence>
        </SettingCard>
      </div>
    </motion.div>
  );
};

export default SettingsPage;
