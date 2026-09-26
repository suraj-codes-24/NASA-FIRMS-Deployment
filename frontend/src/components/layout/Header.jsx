import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Bell, User, Settings, LogOut, AlertCircle, X } from 'lucide-react';
import { fetchReportSummary, fetchCurrentUser, fetchAlerts } from '../../api';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Fetch user state
  const [user, setUser] = useState({ full_name: 'Admin Analyst', role: 'NTRO Security' });
  const [openAlerts, setOpenAlerts] = useState(0);

  useEffect(() => {
    // Try to load from localStorage first for immediate render
    try {
      const storedUser = localStorage.getItem('ignis_user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } catch (e) {
      console.error(e);
    }

    // Fetch the real user from backend to ensure accuracy
    const getUser = async () => {
      try {
        const userData = await fetchCurrentUser();
        if (userData) {
          setUser(userData);
          localStorage.setItem('ignis_user', JSON.stringify(userData)); // update local storage
        }
      } catch (err) {
        console.error("Failed to fetch user", err);
      }
    };
    getUser();
  }, []);

  // Formatting role
  const roleDisplay = user?.role === 'admin' ? 'System Administrator' : (user?.role || 'Analyst');

  // Fetch unread alerts count
  const [alertsList, setAlertsList] = useState([]);
  
  // Dropdown states
  const [showBellDropdown, setShowBellDropdown] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  useEffect(() => {
    const getAlerts = async () => {
      try {
        const summary = await fetchReportSummary();
        if (summary && summary.open_alerts !== undefined) {
          setOpenAlerts(summary.open_alerts);
        }
        
        // Fetch recent alerts for the dropdown
        if (showBellDropdown) {
          const fetchedAlerts = await fetchAlerts();
          setAlertsList(fetchedAlerts.slice(0, 5)); // show top 5
        }
      } catch (err) {
        // silently fail
      }
    };
    getAlerts();
    const interval = setInterval(getAlerts, 30000); 
    return () => clearInterval(interval);
  }, [showBellDropdown]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('.bell-container') && showBellDropdown) setShowBellDropdown(false);
      if (!e.target.closest('.profile-container') && showProfileDropdown) setShowProfileDropdown(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showBellDropdown, showProfileDropdown]);

  const handleLogout = () => {
    localStorage.removeItem('ignis_token');
    localStorage.removeItem('ignis_user');
    window.location.href = '/login';
  };

  const getPageTitle = () => {
    if (location.pathname === '/') return 'Map Dashboard';
    if (location.pathname === '/analytics') return 'Fire Detection Analytics';
    if (location.pathname === '/alerts') return 'Alerts Management';
    if (location.pathname === '/reports') return 'System Reports';
    if (location.pathname === '/settings') return 'System Settings';
    if (location.pathname.startsWith('/hotspot/')) return 'Anomaly Intelligence';
    return 'IGNIS Dashboard';
  };

  return (
    <header className="app-header" style={{ padding: '0 2rem', height: '80px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      
      {/* Dynamic Page Title */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'white', margin: 0, letterSpacing: '0.5px' }}>
          {getPageTitle()}
        </h2>
      </div>

      {/* Empty Center for spacing */}
      <div style={{ flex: 1 }}></div>

      {/* Right Icons & User */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        
        {/* Bell Container */}
        <div className="bell-container" style={{ position: 'relative' }}>
          <button 
            onClick={() => { setShowBellDropdown(!showBellDropdown); setShowProfileDropdown(false); }}
            style={{ width: '36px', height: '36px', borderRadius: '50%', background: showBellDropdown ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', cursor: 'pointer', position: 'relative', transition: 'background 0.2s' }} 
            onMouseEnter={(e) => !showBellDropdown && (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.08)')} 
            onMouseLeave={(e) => !showBellDropdown && (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.03)')}
          >
            <Bell size={16} />
            {openAlerts > 0 && (
              <div style={{ position: 'absolute', top: '8px', right: '8px', width: '6px', height: '6px', backgroundColor: '#ef4444', borderRadius: '50%', boxShadow: '0 0 5px rgba(239, 68, 68, 0.8)' }}></div>
            )}
          </button>
          
          {/* Bell Dropdown */}
          {showBellDropdown && (
            <div style={{ position: 'absolute', top: '48px', right: '0', width: '320px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '12px', boxShadow: '0 10px 40px rgba(0,0,0,0.5)', zIndex: 100, overflow: 'hidden' }}>
              <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: 'white' }}>Recent Alerts</h3>
                <span style={{ fontSize: '11px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '2px 8px', borderRadius: '12px' }}>{openAlerts} New</span>
              </div>
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {alertsList.length === 0 ? (
                  <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '13px' }}>No recent alerts.</div>
                ) : (
                  alertsList.map(alert => (
                    <div key={alert.id} onClick={() => { setShowBellDropdown(false); navigate('/alerts'); }} style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-color)', cursor: 'pointer', display: 'flex', gap: '12px', transition: 'background 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.02)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                      <div style={{ marginTop: '2px' }}><AlertCircle size={16} color={alert.status === 'NEW' ? '#ef4444' : '#2ed573'} /></div>
                      <div>
                        <div style={{ fontSize: '13px', color: 'white', marginBottom: '4px' }}>{alert.severity} Anomaly Detected</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{new Date(alert.created_at).toLocaleString()}</div>
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div onClick={() => { setShowBellDropdown(false); navigate('/alerts'); }} style={{ padding: '12px', textAlign: 'center', fontSize: '13px', color: '#00a8ff', cursor: 'pointer', borderTop: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)' }}>
                View All Alerts
              </div>
            </div>
          )}
        </div>
        
        {/* Profile Container */}
        <div className="profile-container" style={{ position: 'relative' }}>
          <div 
            onClick={() => { setShowProfileDropdown(!showProfileDropdown); setShowBellDropdown(false); }}
            className="user-widget" 
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '6px 12px', borderRadius: '24px', background: showProfileDropdown ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer', transition: 'background 0.2s' }} 
            onMouseEnter={(e) => !showProfileDropdown && (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)')} 
            onMouseLeave={(e) => !showProfileDropdown && (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.02)')}
          >
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'white', display: 'flex', alignItems: 'center' }}>
                {user?.full_name || 'Loading...'}
              </span>
              <span style={{ fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '0.3px', marginTop: '2px', textTransform: 'capitalize' }}>{roleDisplay}</span>
            </div>
            <div style={{ position: 'relative' }}>
              <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: 'linear-gradient(135deg, #00a8ff, #3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', boxShadow: '0 2px 10px rgba(0, 168, 255, 0.3)' }}>
                <User size={16} strokeWidth={2.5} />
              </div>
              <div style={{ position: 'absolute', bottom: '0px', right: '0px', width: '10px', height: '10px', backgroundColor: '#2ed573', borderRadius: '50%', border: '2px solid var(--bg-main)', boxShadow: '0 0 5px rgba(46, 213, 115, 0.5)' }}></div>
            </div>
          </div>
          
          {/* Profile Dropdown */}
          {showProfileDropdown && (
            <div style={{ position: 'absolute', top: '56px', right: '0', width: '220px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '12px', boxShadow: '0 10px 40px rgba(0,0,0,0.5)', zIndex: 100, padding: '8px' }}>
              <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-color)', marginBottom: '8px' }}>
                <div style={{ fontSize: '14px', color: 'white', fontWeight: 600 }}>{user?.full_name}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{user?.email || 'admin@ignis.gov'}</div>
              </div>
              
              <div onClick={() => { setShowProfileDropdown(false); navigate('/settings'); }} style={{ padding: '10px 16px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-secondary)', transition: 'all 0.2s' }} onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)'; e.currentTarget.style.color = 'white'; }} onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}>
                <Settings size={16} />
                <span style={{ fontSize: '13px' }}>Account Settings</span>
              </div>
              
              <div onClick={handleLogout} style={{ padding: '10px 16px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px', color: '#ef4444', transition: 'all 0.2s' }} onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)'; }} onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}>
                <LogOut size={16} />
                <span style={{ fontSize: '13px' }}>Sign Out</span>
              </div>
            </div>
          )}
        </div>
      </div>

    </header>
  );
};

export default Header;
