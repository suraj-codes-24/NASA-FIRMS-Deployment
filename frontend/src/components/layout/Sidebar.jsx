import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import SupportModal from './SupportModal';
import { 
  Grid, 
  Map as MapIcon, 
  BarChart2, 
  FileText, 
  Settings, 
  LogOut,
  HelpCircle,
  Flame
} from 'lucide-react';

const Sidebar = () => {
  const navigate = useNavigate();
  const [showSupport, setShowSupport] = useState(false);
  
  const handleLogout = (e) => {
    e.preventDefault();
    localStorage.removeItem('ignis_token');
    window.location.href = '/';
  };

  return (
    <nav className="app-sidebar">
      <a href="/" style={{ textDecoration: 'none' }}>
        <div className="sidebar-logo" style={{ cursor: 'pointer' }}>
          <div style={{width: '28px', height: '28px', background: 'linear-gradient(135deg, #00a8ff 0%, #3b82f6 100%)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 15px rgba(0,168,255,0.4)'}}>
            <Flame size={16} color="white" />
          </div>
          <span>IGNIS</span>
        </div>
      </a>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%' }}>
        
        <div className="sidebar-section">Surveillance</div>
        <NavLink to="/" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <Grid size={18} />
          <span className="nav-label">Map Dashboard</span>
        </NavLink>
        
        <NavLink to="/alerts" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <MapIcon size={18} />
          <span className="nav-label">Live Alerts</span>
        </NavLink>

        <div className="sidebar-section">Intelligence</div>
        <NavLink to="/analytics" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <BarChart2 size={18} />
          <span className="nav-label">Analytics</span>
        </NavLink>

        <NavLink to="/reports" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <FileText size={18} />
          <span className="nav-label">Reports</span>
        </NavLink>

        <div className="sidebar-section">System</div>
        <NavLink to="/settings" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings size={18} />
          <span className="nav-label">Settings</span>
        </NavLink>
      </div>

      <div style={{ width: '100%', padding: '1rem 0' }}>
        <a href="#" onClick={(e) => { e.preventDefault(); setShowSupport(true); }} className="nav-item">
          <HelpCircle size={18} />
          <span className="nav-label">Help & Support</span>
        </a>
        <a href="#" onClick={handleLogout} className="nav-item" style={{ marginTop: '0.25rem' }}>
          <LogOut size={18} />
          <span className="nav-label">Log Out</span>
        </a>
      </div>

      <SupportModal isOpen={showSupport} onClose={() => setShowSupport(false)} />
    </nav>
  );
};

export default Sidebar;
