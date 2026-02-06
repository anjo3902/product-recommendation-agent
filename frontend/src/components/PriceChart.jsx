// PriceChart.jsx - Beautiful Interactive Price Chart Component
// Similar to pricehistory.app design

import React, { useEffect, useState } from 'react';
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
import annotationPlugin from 'chartjs-plugin-annotation';
import axios from 'axios';
import API_BASE_URL from '../config';
import './PriceChart.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  annotationPlugin
);

const PriceChart = ({ productId, days = 90 }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchChartData();
  }, [productId, days]);

  const fetchChartData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/price/chart/${productId}?days=${days}`
      );

      if (response.data.success) {
        setChartData(response.data.chart);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load price chart');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="price-chart-loading">
        <div className="spinner"></div>
        <p>Loading price history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="price-chart-error">
        <p>{error}</p>
      </div>
    );
  }

  if (!chartData) {
    return null;
  }

  const { statistics, insights, recommendation, annotations, priceZones } = chartData;

  // Chart.js configuration
  const chartConfig = {
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            font: {
              size: 14,
              weight: '500'
            },
            padding: 20
          }
        },
        title: {
          display: true,
          text: `Price Trend - Last ${days} Days`,
          font: {
            size: 20,
            weight: 'bold'
          },
          padding: {
            top: 10,
            bottom: 30
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          },
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (context) => {
              const value = context.parsed.y;
              return `Price: ₹${value.toLocaleString('en-IN')}`;
            }
          }
        },
        annotation: {
          annotations: annotations
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: (value) => `₹${value.toLocaleString('en-IN')}`,
            font: {
              size: 12
            }
          },
          title: {
            display: true,
            text: 'Price (₹)',
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Date',
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 11
            },
            maxRotation: 45,
            minRotation: 0
          }
        }
      }
    }
  };

  return (
    <div className="price-chart-container">
      {/* Chart */}
      <div className="chart-wrapper">
        <Line data={chartConfig.data} options={chartConfig.options} />
      </div>

      {/* Price Statistics Cards */}
      <div className="price-stats-grid">
        <div className="stat-card current">
          <div className="stat-label">Current Price</div>
          <div className="stat-value">₹{statistics.current_price.toLocaleString('en-IN')}</div>
          <div className="stat-badge">Live</div>
        </div>

        <div className="stat-card lowest">
          <div className="stat-label">Lowest Price</div>
          <div className="stat-value">₹{statistics.min_price.toLocaleString('en-IN')}</div>
          <div className="stat-date">{statistics.min_price_date}</div>
        </div>

        <div className="stat-card highest">
          <div className="stat-label">Highest Price</div>
          <div className="stat-value">₹{statistics.max_price.toLocaleString('en-IN')}</div>
          <div className="stat-date">{statistics.max_price_date}</div>
        </div>

        <div className="stat-card average">
          <div className="stat-label">Average Price</div>
          <div className="stat-value">₹{statistics.average_price.toLocaleString('en-IN')}</div>
          <div className="stat-badge">
            {statistics.trend_emoji} {statistics.trend}
          </div>
        </div>
      </div>

      {/* Price Zones Legend */}
      <div className="price-zones">
        <h4>Price Zones</h4>
        <div className="zones-grid">
          {priceZones.map((zone, index) => (
            <div key={index} className="zone-item">
              <span
                className="zone-color"
                style={{ backgroundColor: zone.color, borderColor: zone.borderColor }}
              ></span>
              <span className="zone-name">{zone.name}</span>
              <span className="zone-range">
                ₹{zone.min.toLocaleString('en-IN')} - ₹{zone.max.toLocaleString('en-IN')}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Insights */}
      <div className="insights-section">
        <h4>Insights</h4>
        <ul className="insights-list">
          {insights.map((insight, index) => (
            <li key={index}>{insight}</li>
          ))}
        </ul>
      </div>

      {/* Recommendation */}
      <div className={`recommendation-card ${recommendation.action}`}>
        <div className="rec-emoji">{recommendation.emoji}</div>
        <div className="rec-content">
          <h3>{recommendation.text}</h3>
          <p>{recommendation.reason}</p>
        </div>
      </div>

      {/* Additional Stats */}
      <div className="additional-stats">
        <div className="stat-item">
          <span className="label">Price Range:</span>
          <span className="value">₹{statistics.price_range.toLocaleString('en-IN')}</span>
        </div>
        <div className="stat-item">
          <span className="label">Volatility:</span>
          <span className="value">{statistics.volatility}%</span>
        </div>
        <div className="stat-item">
          <span className="label">Trend:</span>
          <span className="value">
            {statistics.trend_emoji} {statistics.trend_percentage > 0 ? '+' : ''}
            {statistics.trend_percentage}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default PriceChart;
