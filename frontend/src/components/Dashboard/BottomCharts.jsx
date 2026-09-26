import React from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  LogarithmicScale
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  LogarithmicScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#a0aec0', boxWidth: 12, padding: 15, font: { size: 11, family: 'Inter' } },
      position: 'top',
    }
  },
  scales: {
    x: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { color: '#718096', font: { size: 10 } }
    },
    y: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { color: '#718096', font: { size: 10 } }
    }
  }
};

const BottomCharts = () => {
  // Data for Line Chart (Comparison Chart: Thermal Signatures) - Needs Logarithmic Y and X roughly
  const lineData = {
    labels: ['0.1', '1', '10', '100'], // Wavelength (um)
    datasets: [
      {
        label: 'Industrial Fire',
        data: [0.1, 150, 15, 0.5],
        borderColor: '#ef4444',
        backgroundColor: '#ef4444',
        tension: 0.4,
        pointRadius: 0
      },
      {
        label: 'Vegetation Fire',
        data: [0.05, 10, 2, 0.2],
        borderColor: '#ffa502',
        backgroundColor: '#ffa502',
        tension: 0.4,
        pointRadius: 0
      },
      {
        label: 'Non-Fire Heat Source',
        data: [0.01, 1, 0.5, 0.1],
        borderColor: '#eccc68',
        backgroundColor: '#eccc68',
        tension: 0.4,
        pointRadius: 0
      }
    ],
  };

  const lineOptions = {
    ...chartOptions,
    scales: {
      x: { ...chartOptions.scales.x, title: { display: true, text: 'Wavelength (μm)', color: '#718096', font: { size: 10 } } },
      y: { ...chartOptions.scales.y, type: 'logarithmic', title: { display: true, text: 'Spectral Radiance', color: '#718096', font: { size: 10 } } }
    }
  };

  // Data for Bar Chart (Timeline)
  const barData = {
    labels: Array.from({length: 30}, (_, i) => (i + 1).toString()),
    datasets: [
      {
        label: 'Industrial Fire',
        data: Array.from({length: 30}, () => Math.floor(Math.random() * 40)),
        backgroundColor: '#ef4444'
      },
      {
        label: 'Vegetation Fire',
        data: Array.from({length: 30}, () => Math.floor(Math.random() * 60)),
        backgroundColor: '#ffa502'
      }
    ]
  };

  const barOptions = {
    ...chartOptions,
    plugins: {
      legend: { display: false } // Custom text handles legend here
    },
    scales: {
      x: { stacked: true, grid: { display: false }, ticks: { color: '#718096', font: { size: 10 } }, title: { display: true, text: 'September', color: '#718096', font: { size: 10 } } },
      y: { stacked: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#718096', font: { size: 10 } }, title: { display: true, text: 'Number of detection events', color: '#718096', font: { size: 10 } } }
    }
  };

  // Data for Donut Chart (Classification Breakdown)
  const donutData = {
    labels: ['Industrial Fire', 'Vegetation Fire', 'Managed Agricultural', 'Non-Fire Event'],
    datasets: [
      {
        data: [45, 32, 12, 11],
        backgroundColor: ['#ef4444', '#ffa502', '#eccc68', '#718096'],
        borderWidth: 0,
        hoverOffset: 4
      }
    ]
  };

  const donutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: { display: false } // We'll build custom legend below
    }
  };

  return (
    <div style={{ position: 'absolute', bottom: '20px', left: '20px', right: '20px', display: 'flex', gap: '20px', zIndex: 1000, height: '240px' }}>
      
      {/* Chart 1: Comparison */}
      <div className="glass-panel" style={{ flex: 1, padding: '15px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.5px' }}>COMPARISON CHART: THERMAL SIGNATURES</h3>
          <span style={{ color: 'var(--text-muted)' }}>...</span>
        </div>
        <div style={{ flex: 1, position: 'relative' }}>
          <Line options={lineOptions} data={lineData} />
        </div>
      </div>

      {/* Chart 2: Timeline */}
      <div className="glass-panel" style={{ flex: 1.2, padding: '15px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.5px' }}>TIMELINE: HOTSPOT ACTIVITY (30 DAYS)</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total Hotspots (30d): <strong style={{color:'white'}}>112</strong></span>
            <span style={{ color: 'var(--text-muted)' }}>...</span>
          </div>
        </div>
        <div style={{ flex: 1, position: 'relative' }}>
          <Bar options={barOptions} data={barData} />
        </div>
      </div>

      {/* Chart 3: Breakdown */}
      <div className="glass-panel" style={{ width: '320px', padding: '15px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.5px' }}>CLASSIFICATION BREAKDOWN</h3>
          <span style={{ color: 'var(--text-muted)' }}>...</span>
        </div>
        <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ width: '140px', height: '140px', position: 'relative' }}>
             <Doughnut options={donutOptions} data={donutData} />
             {/* Center labels can be added here if needed */}
          </div>
        </div>
        {/* Custom Legend */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', fontSize: '11px', color: 'var(--text-secondary)', marginTop: '10px', justifyContent: 'center' }}>
           <div style={{display:'flex', alignItems:'center', gap:'4px'}}><div style={{width:'8px',height:'8px',borderRadius:'50%',backgroundColor:'#ef4444'}}></div>Industrial Fire</div>
           <div style={{display:'flex', alignItems:'center', gap:'4px'}}><div style={{width:'8px',height:'8px',borderRadius:'50%',backgroundColor:'#ffa502'}}></div>Vegetation Fire</div>
           <div style={{display:'flex', alignItems:'center', gap:'4px'}}><div style={{width:'8px',height:'8px',borderRadius:'50%',backgroundColor:'#eccc68'}}></div>Managed Agricultural</div>
           <div style={{display:'flex', alignItems:'center', gap:'4px'}}><div style={{width:'8px',height:'8px',borderRadius:'50%',backgroundColor:'#718096'}}></div>Non-Fire Event</div>
        </div>
      </div>

    </div>
  );
};

export default BottomCharts;
