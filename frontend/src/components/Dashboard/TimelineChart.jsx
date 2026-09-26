/**
 * Dashboard/TimelineChart.jsx
 * 
 * Re-exports the timeline section from BottomCharts.
 * Spec §9.3 requires Dashboard/TimelineChart.jsx.
 */
import React from 'react';
import { Line } from 'react-chartjs-2';

const TimelineChart = ({ data = [], label = 'Fire Detections' }) => {
  const chartData = {
    labels: data.map(d => d.date || d.label),
    datasets: [{
      label,
      data: data.map(d => d.count || d.value),
      borderColor: '#e74c3c',
      backgroundColor: 'rgba(231, 76, 60, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 5,
      borderWidth: 2,
    }],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(26, 31, 58, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        titleColor: '#fff',
        bodyColor: 'rgba(255,255,255,0.8)',
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: { color: 'rgba(255, 255, 255, 0.4)', maxTicksLimit: 8, font: { size: 10 } },
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.04)' },
        ticks: { color: 'rgba(255, 255, 255, 0.4)', font: { size: 10 } },
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="glass-panel" style={{ padding: '16px', borderRadius: '12px', height: '250px' }}>
      <h4 style={{ margin: '0 0 12px', fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
        Detection Timeline
      </h4>
      <div style={{ height: 'calc(100% - 32px)' }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

export default TimelineChart;
