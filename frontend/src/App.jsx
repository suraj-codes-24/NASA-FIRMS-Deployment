import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import SplashScreen from './components/layout/SplashScreen';
import MapDashboard from './pages/MapDashboard';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AlertsDashboard from './pages/AlertsDashboard';
import HotspotDetailPage from './pages/HotspotDetailPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import useWebSocket from './hooks/useWebSocket';
import { WS_BASE } from './config';
import { SettingsProvider } from './contexts/SettingsContext';
import './App.css';

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -12 },
};

const pageTransition = { duration: 0.25, ease: 'easeInOut' };

function PageWrapper({ children }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={pageTransition}
      style={{ height: '100%', width: '100%' }}
    >
      {children}
    </motion.div>
  );
}

function AppLayout({ children }) {
  // Connect WebSocket for real-time alerts
  useWebSocket(WS_BASE + '/alerts');

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-main">
        <Header />
        <div className="app-content">
          {children}
        </div>
      </main>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('ignis_token');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function AnimatedRoutes() {
  const location = useLocation();


  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Login page — no sidebar/header layout */}
        <Route path="/login" element={<PageWrapper><LoginPage /></PageWrapper>} />

        {/* All dashboard routes wrapped in AppLayout and ProtectedRoute */}
        <Route path="/" element={<ProtectedRoute><AppLayout><PageWrapper><MapDashboard /></PageWrapper></AppLayout></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><AppLayout><PageWrapper><AnalyticsDashboard /></PageWrapper></AppLayout></ProtectedRoute>} />
        <Route path="/alerts" element={<ProtectedRoute><AppLayout><PageWrapper><AlertsDashboard /></PageWrapper></AppLayout></ProtectedRoute>} />
        <Route path="/hotspot/:id" element={<ProtectedRoute><AppLayout><PageWrapper><HotspotDetailPage /></PageWrapper></AppLayout></ProtectedRoute>} />
        <Route path="/reports" element={<ProtectedRoute><AppLayout><PageWrapper><ReportsPage /></PageWrapper></AppLayout></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><AppLayout><PageWrapper><SettingsPage /></PageWrapper></AppLayout></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  const [booting, setBooting] = useState(() => {
    return !sessionStorage.getItem('ignis_booted');
  });

  const handleBootComplete = () => {
    sessionStorage.setItem('ignis_booted', 'true');
    setBooting(false);
  };

  return (
    <SettingsProvider>
      {booting && <SplashScreen onComplete={handleBootComplete} />}
      <BrowserRouter>
        <AnimatedRoutes />
      </BrowserRouter>
    </SettingsProvider>
  );
}

export default App;
