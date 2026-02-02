import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import API_BASE_URL from '../config';
import { getApiHeaders } from '../utils/api';
import './ForYou.css';

/**
 * For You - Personalized Recommendations Page
 * Production-ready with professional design
 */
const ForYou = () => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      fetchRecommendations();
    } else {
      setLoading(false);
      setError('Please log in to see personalized recommendations');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const fetchRecommendations = async () => {
    if (!token) {
      setError('Please log in to see personalized recommendations');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${API_BASE_URL}/recommendations/for-you`, {
        headers: getApiHeaders(token),
      });

      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
          // Check if it's ngrok warning page
          const text = await response.text();
          if (text.includes('ngrok') || text.includes('tunnel')) {
            throw new Error(`NGROK_BLOCKED:${API_BASE_URL}`);
          }
          throw new Error('Unable to connect to server. Please check if backend is running.');
        }
        throw new Error('Failed to fetch recommendations');
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server returned invalid response. Backend may be offline.');
      }

      const data = await response.json();
      setRecommendations(data);
    } catch (err) {
      if (err.message && err.message.startsWith('NGROK_BLOCKED:')) {
        const ngrokUrl = err.message.split(':')[1] + ':' + err.message.split(':')[2];
        setError(`ngrok_warning:${ngrokUrl}`);
      } else if (err.name === 'SyntaxError') {
        setError('Connection error: Backend server is not responding correctly. Please ensure your laptop is on with Ollama, backend, and ngrok running.');
      } else {
        setError(err.message);
      }
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToWishlist = async (product) => {
    try {
      const response = await fetch(`${API_BASE_URL}/preferences/wishlist`, {
        method: 'POST',
        headers: getApiHeaders(token, { 'Content-Type': 'application/json' }),
        body: JSON.stringify({ product_id: product.id }),
      });

      if (response.ok) {
        alert('Added to wishlist! ❤️');
      }
    } catch (err) {
      console.error('Error adding to wishlist:', err);
    }
  };

  const handleViewDetails = (product) => {
    // TODO: Navigate to product details page
    console.log('View product:', product);
    alert(`Product Details: ${product.name}\nPrice: $${product.price}\nRating: ${product.rating}`);
  };

  if (loading) {
    return (
      <div className="for-you-container">
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Finding perfect recommendations for you...</p>
        </div>
      </div>
    );
  }

  if (error) {
    // Check if it's ngrok warning error
    if (error.startsWith('ngrok_warning:')) {
      const ngrokUrl = error.replace('ngrok_warning:', '');
      return (
        <div className="for-you-container">
          <div className="error-state">
            <div className="error-icon">🔧</div>
            <h3>Backend Setup Required</h3>
            <p>Your backend server is running but needs browser authentication.</p>
            <div style={{ textAlign: 'left', maxWidth: '600px', margin: '20px auto', padding: '20px', background: '#f0f0f0', borderRadius: '8px' }}>
              <h4>📋 Quick Fix (One-time setup):</h4>
              <ol style={{ lineHeight: '1.8' }}>
                <li>Open this link in a NEW TAB: <a href={`${ngrokUrl}/docs`} target="_blank" rel="noopener noreferrer" style={{ color: '#007bff', fontWeight: 'bold' }}>{ngrokUrl}/docs</a></li>
                <li>Click "Visit Site" on the warning page</li>
                <li>Come back to this tab</li>
                <li>Click "Try Again" below</li>
              </ol>
              <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
                💡 <strong>Why?</strong> Your laptop uses ngrok to make the backend accessible. This is a one-time authentication.
              </p>
            </div>
            <button className="btn btn-primary" onClick={fetchRecommendations}>
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="for-you-container">
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Oops! Something went wrong</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchRecommendations}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!recommendations) {
    return null;
  }

  const renderSection = (title, products, icon, color) => {
    // Ensure products is an array
    if (!products || !Array.isArray(products) || products.length === 0) return null;

    return (
      <section className="recommendation-section">
        <div className="section-header">
          <div className="section-title">
            <span className="section-icon" style={{ color }}>{icon}</span>
            <h2>{title}</h2>
          </div>
          <span className="section-count">{products.length} items</span>
        </div>
        <div className="products-grid">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToWishlist={handleAddToWishlist}
              onViewDetails={handleViewDetails}
              showRecommendationScore={true}
            />
          ))}
        </div>
      </section>
    );
  };

  return (
    <div className="for-you-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1>✨ Personalized For You</h1>
          <p>Handpicked recommendations based on your preferences and shopping history</p>
        </div>
        {recommendations.insights && (
          <div className="insights-card">
            <h3>📊 Your Shopping Insights</h3>
            <div className="insights-grid">
              <div className="insight-item">
                <div className="insight-value">{recommendations.insights.total_recommendations}</div>
                <div className="insight-label">Recommendations</div>
              </div>
              <div className="insight-item">
                <div className="insight-value">{recommendations.insights.sections_count}</div>
                <div className="insight-label">Categories</div>
              </div>
              <div className="insight-item">
                <div className="insight-value">
                  {recommendations.insights.avg_score ?
                    `${Math.round(recommendations.insights.avg_score * 100)}%` :
                    'N/A'}
                </div>
                <div className="insight-label">Match Score</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recommendation Sections */}
      <div className="sections-container">
        {renderSection(
          'Based on Your Wishlist',
          recommendations.wishlist_recommendations,
          '❤️',
          '#e53e3e'
        )}

        {renderSection(
          'Similar to What You Searched',
          recommendations.search_based_recommendations,
          '🔍',
          '#667eea'
        )}

        {renderSection(
          'Trending Now',
          recommendations.trending_products,
          '🔥',
          '#f56565'
        )}

        {renderSection(
          'Popular in Your Favorite Categories',
          recommendations.category_recommendations,
          '⭐',
          '#ed8936'
        )}

        {renderSection(
          'People Also Like',
          recommendations.collaborative_recommendations,
          '👥',
          '#48bb78'
        )}

        {/* No Recommendations */}
        {(!Array.isArray(recommendations.wishlist_recommendations) || !recommendations.wishlist_recommendations.length) &&
          (!Array.isArray(recommendations.search_based_recommendations) || !recommendations.search_based_recommendations.length) &&
          (!Array.isArray(recommendations.trending_products) || !recommendations.trending_products.length) &&
          (!Array.isArray(recommendations.category_recommendations) || !recommendations.category_recommendations.length) &&
          (!Array.isArray(recommendations.collaborative_recommendations) || !recommendations.collaborative_recommendations.length) && (
            <div className="empty-state">
              <div className="empty-icon">🎯</div>
              <h3>Start Your Journey</h3>
              <p>Add products to your wishlist or search for items to get personalized recommendations!</p>
            </div>
          )}
      </div>

      {/* Refresh Button */}
      <div className="refresh-section">
        <button className="btn btn-outline" onClick={fetchRecommendations}>
          🔄 Refresh Recommendations
        </button>
      </div>
    </div>
  );
};

export default ForYou;
