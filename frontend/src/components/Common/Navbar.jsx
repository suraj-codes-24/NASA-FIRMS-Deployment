import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import IconButton from '@mui/material/IconButton'
import Badge from '@mui/material/Badge'
import { Flame, BarChart3, Bell, FileText, Settings, MapPin } from 'lucide-react'

const navItems = [
  { label: 'Dashboard', path: '/', icon: <MapPin size={18} /> },
  { label: 'Analytics', path: '/analytics', icon: <BarChart3 size={18} /> },
  { label: 'Alerts', path: '/alerts', icon: <Bell size={18} /> },
  { label: 'Reports', path: '/reports', icon: <FileText size={18} /> },
  { label: 'Settings', path: '/settings', icon: <Settings size={18} /> },
]

export default function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        background: 'rgba(10, 14, 39, 0.85)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: 3 }}>
        {/* Logo */}
        <Box
          sx={{ display: 'flex', alignItems: 'center', gap: 1.5, cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          <Flame size={28} color="#e74c3c" />
          <Typography
            variant="h6"
            sx={{
              fontFamily: '"Inter", sans-serif',
              fontWeight: 800,
              letterSpacing: '0.05em',
              background: 'linear-gradient(135deg, #e74c3c, #f39c12)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            IGNIS
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255,255,255,0.5)',
              fontFamily: '"Roboto", sans-serif',
              display: { xs: 'none', md: 'block' },
            }}
          >
            Industrial Fire Surveillance
          </Typography>
        </Box>

        {/* Navigation */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          {navItems.map((item) => (
            <Box
              key={item.path}
              onClick={() => navigate(item.path)}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.75,
                px: 2,
                py: 1,
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                color: location.pathname === item.path
                  ? '#e74c3c'
                  : 'rgba(255,255,255,0.6)',
                backgroundColor: location.pathname === item.path
                  ? 'rgba(231, 76, 60, 0.1)'
                  : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.05)',
                  color: '#fff',
                },
                fontFamily: '"Inter", sans-serif',
                fontSize: '0.85rem',
                fontWeight: 500,
              }}
            >
              {item.label === 'Alerts' ? (
                <Badge badgeContent={0} color="error" variant="dot">
                  {item.icon}
                </Badge>
              ) : (
                item.icon
              )}
              <Box sx={{ display: { xs: 'none', lg: 'block' } }}>
                {item.label}
              </Box>
            </Box>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  )
}
