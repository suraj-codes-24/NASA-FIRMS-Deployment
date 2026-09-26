import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { fetchAnalyticsTimeline } from '../../api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top',
      align: 'end',
      labels: {
        color: '#a0aec0',
        usePointStyle: true,
        pointStyle: 'circle',
        boxWidth: 8,
        padding: 20,
        font: { size: 12, family: 'Inter, sans-serif', weight: 500 }
      }
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(15, 17, 26, 0.9)',
      titleColor: '#fff',
      bodyColor: '#a0aec0',
      borderColor: 'rgba(255,255,255,0.1)',
      borderWidth: 1,
      padding: 12,
      boxPadding: 6,
      usePointStyle: true,
      titleFont: { size: 13, family: 'Inter', weight: 600 },
      bodyFont: { size: 12, family: 'Inter' }
    },
  },
  scales: {
    x: {
      border: { display: false },
      grid: { color: 'rgba(255,255,255,0.03)' },
      ticks: { color: '#718096', font: { size: 11, family: 'Inter' }, padding: 10 }
    },
    y: {
      border: { display: false },
      grid: { color: 'rgba(255,255,255,0.03)' },
      ticks: { color: '#718096', font: { size: 11, family: 'Inter' }, padding: 10 },
      beginAtZero: true
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
};

const FrequencyChart = ({ filters }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const activeFilters = {};
        if (filters?.date_from) activeFilters.date_from = filters.date_from;
        if (filters?.date_to) activeFilters.date_to = filters.date_to;
        if (filters?.ml_label) activeFilters.ml_label = filters.ml_label;
        if (filters?.min_confidence > 0) activeFilters.min_confidence = filters.min_confidence;

        const rawData = await fetchAnalyticsTimeline(activeFilters);

        // 1. Extract all unique dates and sort them
        const datesSet = new Set();
        rawData.forEach(item => datesSet.add(item.date));
        const sortedDates = Array.from(datesSet).sort();
        
        // Use last 14 days of data available (or less)
        const labels = sortedDates.slice(-14);
        
        // 2. Initialize dataset arrays
        const miningData = labels.map(() => 0);
        const agriData = labels.map(() => 0);
        const gasData = labels.map(() => 0);
        const industrialData = labels.map(() => 0);

        // 3. Fill datasets
        rawData.forEach(item => {
          const dateIndex = labels.indexOf(item.date);
          if (dateIndex !== -1) {
            const label = item.ml_label || '';
            if (label === 'Mining/Thermal' || label === 'MINING_THERMAL') {
              miningData[dateIndex] += item.count;
            } else if (label === 'Agricultural Burn' || label === 'AGRICULTURAL_BURN') {
              agriData[dateIndex] += item.count;
            } else if (label === 'Gas Flare' || label === 'GAS_FLARE') {
              gasData[dateIndex] += item.count;
            } else if (label === 'Industrial Fire' || label === 'INDUSTRIAL_FIRE') {
              industrialData[dateIndex] += item.count;
            }
          }
        });

        // Add formatted date labels
        const formattedLabels = labels.map(d => {
          const dateObj = new Date(d);
          return dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        setChartData({
          labels: formattedLabels,
          datasets: [
            {
              label: 'Industrial Fire',
              data: industrialData,
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              borderWidth: 2,
              tension: 0.4,
              pointRadius: 0,
              pointHoverRadius: 6,
              fill: true,
            },
            {
              label: 'Mining & Thermal',
              data: miningData,
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              borderWidth: 2,
              tension: 0.4,
              pointRadius: 0,
              pointHoverRadius: 6,
              fill: true,
            },
            {
              label: 'Agricultural Burn',
              data: agriData,
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderWidth: 2,
              tension: 0.4,
              pointRadius: 0,
              pointHoverRadius: 6,
              fill: true,
            },
            {
              label: 'Gas Flare',
              data: gasData,
              borderColor: '#eab308',
              backgroundColor: 'rgba(234, 179, 8, 0.1)',
              borderWidth: 2,
              tension: 0.4,
              pointRadius: 0,
              pointHoverRadius: 6,
              fill: true,
            }
          ],
        });
        console.log("Chart Data Set Successfully:", formattedLabels, industrialData, miningData);
      } catch (err) {
        console.error("Failed to load chart data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [filters]);

  if (!chartData) return <div className="glass-panel" style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading Chart Data...</div>;

  return (
    <div className="glass-panel" style={{ height: '320px', padding: '20px 24px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, letterSpacing: '0.5px', color: '#fff', display: 'flex', alignItems: 'center', gap: '12px' }}>
          Anomaly Frequency (14-Day Trend)
          {loading && <Loader2 size={14} color="#00a8ff" className="spin" />}
        </h3>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '4px 10px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
          Real-time API
        </span>
      </div>
      <div style={{ flex: 1, position: 'relative' }}>
        {chartData && chartData.labels && chartData.labels.length > 0 ? (
          <Line options={chartOptions} data={chartData} />
        ) : (
          <div style={{ color: 'var(--text-muted)' }}>No historical data available.</div>
        )}
      </div>
    </div>
  );
};

export default FrequencyChart;
