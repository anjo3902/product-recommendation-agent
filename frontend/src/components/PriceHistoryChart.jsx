import React, { useState, useEffect, useRef } from 'react';
import './PriceHistoryChart.css';

const PriceHistoryChart = ({ productName, priceData }) => {
  const canvasRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [chartData, setChartData] = useState(null);
  const [stats, setStats] = useState({
    lowest: 0,
    average: 0,
    highest: 0,
    current: 0,
    recommendation: 'Wait'
  });

  useEffect(() => {
    if (priceData && priceData.chart_data) {
      // Handle both Chart.js format (datasets) and simple array format (data)
      // Backend provides: chart_data.datasets[0].data (Chart.js format)
      // Fallback to: chart_data.data (simple format for backward compatibility)
      let prices = [];
      let labels = [];

      if (priceData.chart_data.datasets && priceData.chart_data.datasets.length > 0) {
        // Chart.js format: extract from first dataset
        prices = priceData.chart_data.datasets[0].data || [];
        labels = priceData.chart_data.labels || [];
      } else {
        // Simple format (fallback)
        prices = priceData.chart_data.data || [];
        labels = priceData.chart_data.labels || [];
      }

      if (prices.length > 0) {
        // PRODUCTION FIX: Add current price to chart if it's different from last historical price
        const current = priceData.current_price || prices[prices.length - 1];
        const lastHistoricalPrice = prices[prices.length - 1];

        // If current price is different, append it to show the price change
        if (current !== lastHistoricalPrice && priceData.current_price) {
          prices = [...prices, current];
          labels = [...labels, 'Today'];
        }

        const lowest = Math.min(...prices);
        const highest = Math.max(...prices);
        const average = prices.reduce((a, b) => a + b, 0) / prices.length;

        setStats({
          lowest,
          average,
          highest,
          current,
          recommendation: priceData.recommendation || 'Wait'
        });

        setChartData({ prices, labels });
      }
    }
  }, [priceData]);

  useEffect(() => {
    if (!chartData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { prices, labels } = chartData;

    // Set canvas size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const width = rect.width;
    const height = rect.height;
    const padding = { top: 30, right: 30, bottom: 50, left: 60 };

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Calculate chart dimensions
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    let priceRange = maxPrice - minPrice;

    // FIX: When all prices are the same, priceRange = 0, causing invisible line
    // Add minimum range of 10% of the price to make the line visible
    if (priceRange === 0) {
      priceRange = maxPrice * 0.1 || 100; // 10% of price, or 100 if price is 0
    }

    // Helper function to get Y position
    const getY = (price) => {
      // Center the line when prices are constant
      if (maxPrice === minPrice) {
        return padding.top + chartHeight / 2;
      }
      return padding.top + chartHeight - ((price - minPrice) / priceRange) * chartHeight;
    };

    // Helper function to get X position
    const getX = (index) => {
      return padding.left + (index / (prices.length - 1)) * chartWidth;
    };

    // Draw grid lines
    ctx.strokeStyle = 'rgba(100, 149, 237, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding.top + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();
    }

    // Draw Y-axis labels
    ctx.fillStyle = '#7c8db5';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
      const price = maxPrice - (priceRange / 5) * i;
      const y = padding.top + (chartHeight / 5) * i;
      ctx.fillText(`₹${Math.round(price / 1000)}k`, padding.left - 10, y + 4);
    }

    // Draw bars (for price drops/spikes)
    const barWidth = Math.max(chartWidth / prices.length - 4, 8);
    prices.forEach((price, index) => {
      const x = getX(index);
      const y = getY(price);
      const barHeight = chartHeight - (y - padding.top);

      // Create gradient for bars
      const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartHeight);
      gradient.addColorStop(0, 'rgba(100, 149, 237, 0.8)');
      gradient.addColorStop(1, 'rgba(100, 149, 237, 0.2)');

      ctx.fillStyle = gradient;
      ctx.fillRect(x - barWidth / 2, y, barWidth, barHeight);
    });

    // Draw smooth line connecting prices
    ctx.beginPath();
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 3;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    prices.forEach((price, index) => {
      const x = getX(index);
      const y = getY(price);

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        // Smooth curve using quadratic bezier
        const prevX = getX(index - 1);
        const prevY = getY(prices[index - 1]);
        const cpX = (prevX + x) / 2;
        ctx.quadraticCurveTo(prevX, prevY, cpX, (prevY + y) / 2);
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw data points
    prices.forEach((price, index) => {
      const x = getX(index);
      const y = getY(price);

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#4CAF50';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2;
      ctx.stroke();
    });

    // Draw X-axis labels (dates)
    ctx.fillStyle = '#7c8db5';
    ctx.font = '11px Arial';
    ctx.textAlign = 'center';
    const step = Math.ceil(labels.length / 8);
    labels.forEach((label, index) => {
      if (index % step === 0) {
        const x = getX(index);
        const date = new Date(label);
        const dateStr = `${date.getDate()}/${date.getMonth() + 1}`;
        ctx.fillText(dateStr, x, height - padding.bottom + 20);
      }
    });

  }, [chartData]);

  const getBuyRecommendationPosition = () => {
    if (!stats.current || !stats.lowest || !stats.highest) return 50;

    const range = stats.highest - stats.lowest;
    const position = ((stats.current - stats.lowest) / range) * 100;
    return Math.min(Math.max(position, 0), 100);
  };

  const getBuyRecommendationText = () => {
    const position = getBuyRecommendationPosition();
    if (position < 25) return { text: 'Yes', color: '#4CAF50', description: 'Great deal! Price is near the lowest.' };
    if (position < 50) return { text: 'Okay', color: '#8BC34A', description: 'Good price, consider buying.' };
    if (position < 75) return { text: 'Wait', color: '#FF9800', description: 'Price is average, wait for a better deal.' };
    return { text: 'Skip', color: '#f44336', description: 'Price is high, skip for now.' };
  };

  const recommendation = getBuyRecommendationText();

  const downloadChart = () => {
    if (!canvasRef.current) return;
    const link = document.createElement('a');
    link.download = `${productName}-price-history.png`;
    link.href = canvasRef.current.toDataURL();
    link.click();
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!chartData) {
    return (
      <div className="price-history-chart-container">
        <p className="no-data">No price history data available</p>
      </div>
    );
  }

  const changePct = stats.current && stats.average
    ? (((stats.current - stats.average) / stats.average) * 100).toFixed(1)
    : 0;

  return (
    <div className={`price-history-chart-container ${isFullscreen ? 'fullscreen' : ''}`}>
      {/* Buy Recommendation Slider */}
      <div className="buy-recommendation-section">
        <h3>Should you buy at this price?</h3>
        <div className="recommendation-slider">
          <div className="slider-labels">
            <span>Skip</span>
            <span>Wait</span>
            <span>Okay</span>
            <span>Yes</span>
          </div>
          <div className="slider-track">
            <div
              className="slider-thumb"
              style={{ left: `${getBuyRecommendationPosition()}%` }}
            >
              <div className="thumb-marker"></div>
            </div>
          </div>
        </div>
        <div className="recommendation-text" style={{ color: recommendation.color }}>
          <strong>{recommendation.text}</strong>
          <p>{recommendation.description}</p>
        </div>
        <p className="price-analysis-text">
          Based on our analysis, the price might fluctuate between{' '}
          <strong>{Math.abs(changePct)}%</strong> of current price.
          Current: <strong>₹{Math.round(stats.current)}</strong> |
          Average: <strong>₹{Math.round(stats.average)}</strong>
        </p>
      </div>

      {/* Price History Chart */}
      <div className="chart-section">
        <div className="chart-header">
          <h3>Price History Graph</h3>
          <div className="chart-controls">
            <button onClick={downloadChart} className="control-btn" title="Download Chart">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <button onClick={toggleFullscreen} className="control-btn" title="Toggle Fullscreen">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>

        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-color" style={{ background: '#4CAF50' }}></span>
            <span>Prices</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: 'rgba(100, 149, 237, 0.6)' }}></span>
            <span>Price Range</span>
          </div>
        </div>

        <div className="chart-canvas-wrapper">
          <canvas ref={canvasRef} className="price-chart-canvas"></canvas>
        </div>

        <div className="chart-stats">
          <div className="stat-item stat-lowest">
            <span className="stat-label">Lowest:</span>
            <span className="stat-value">₹{Math.round(stats.lowest)}</span>
          </div>
          <div className="stat-item stat-average">
            <span className="stat-label">Average:</span>
            <span className="stat-value">₹{Math.round(stats.average)}</span>
          </div>
          <div className="stat-item stat-highest">
            <span className="stat-label">Highest:</span>
            <span className="stat-value">₹{Math.round(stats.highest)}</span>
          </div>
        </div>
      </div>

      {/* Price Information Table */}
      <div className="price-info-section">
        <h4>Price History Information</h4>
        <p className="info-description">
          Current Price in India is <strong>₹{Math.round(stats.current)}</strong>.
          The average and highest prices are <strong>₹{Math.round(stats.average)}</strong> and{' '}
          <strong>₹{Math.round(stats.highest)}</strong> respectively.
        </p>
        <table className="price-info-table">
          <tbody>
            <tr>
              <td className="info-label">Lowest Ever Price</td>
              <td className="info-value">₹{Math.round(stats.lowest)}</td>
            </tr>
            <tr>
              <td className="info-label">Average Price</td>
              <td className="info-value">₹{Math.round(stats.average)}</td>
            </tr>
            <tr>
              <td className="info-label">Highest Price</td>
              <td className="info-value">₹{Math.round(stats.highest)}</td>
            </tr>
            <tr>
              <td className="info-label">Based on</td>
              <td className="info-value">{chartData.prices.length} days price tracking</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PriceHistoryChart;
