import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import ProductDetailsModal from './ProductDetailsModal';
import './Recommendations.css';

/**
 * Recommendations Display Component - Amazon/Flipkart Style
 * Automatic personalized recommendations without user configuration
 */
const Recommendations = () => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    fetchRecommendations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError('');

      // Use hybrid strategy by default (best results like Amazon/Flipkart)
      const url = `http://localhost:8000/recommendations/personalized?strategy=hybrid&limit=50`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToWishlist = async (product) => {
    try {
      // API returns 'product_id', not 'id'
      const productId = product.product_id || product.id;

      if (!productId) {
        alert('Error: Product ID not found');
        console.error('Product object:', product);
        return;
      }

      const response = await fetch('http://localhost:8000/preferences/wishlist', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId }),
      });

      if (response.ok) {
        alert('✅ Added to wishlist!');
        // Refresh recommendations after wishlist update
        fetchRecommendations();
      } else {
        const errorData = await response.json();
        if (response.status === 400 && errorData.detail?.includes('already in wishlist')) {
          alert('ℹ️ This product is already in your wishlist');
        } else {
          alert(`❌ Failed to add to wishlist: ${errorData.detail || 'Unknown error'}`);
        }
      }
    } catch (err) {
      console.error('Error adding to wishlist:', err);
      alert('❌ Network error. Please check your connection.');
    }
  };

  const handleViewDetails = (product) => {
    console.log('View product:', product);
    setSelectedProduct(product);
  };

  return (
    <div className="recommendations-container">
      {/* Simple Header - Like Amazon */}
      <div className="recommendations-header-simple">
        <h1>✨ Recommended for you</h1>
        <p>Based on your shopping activity</p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner-large"></div>
          <p>Finding perfect products for you...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button onClick={fetchRecommendations}>Try Again</button>
        </div>
      )}

      {/* Results - Clean Grid Like Amazon/Flipkart */}
      {!loading && !error && (
        <>
          {Array.isArray(recommendations) && recommendations.length > 0 ? (
            <div className="products-grid-clean">
              {recommendations.map((product) => (
                <ProductCard
                  key={product.product_id || product.id}
                  product={product}
                  onAddToWishlist={handleAddToWishlist}
                  onViewDetails={handleViewDetails}
                  showRecommendationScore={false}
                />
              ))}
            </div>
          ) : (
            <div className="empty-state-clean">
              <div className="empty-icon">🛍️</div>
              <h3>Start Your Shopping Journey</h3>
              <p>
                Search for products or add items to your wishlist to get personalized recommendations
              </p>
              <button className="btn-primary" onClick={() => window.location.href = '#'}>
                Browse Products
              </button>
            </div>
          )}
        </>
      )}

      {/* Product Details Modal */}
      {selectedProduct && (
        <ProductDetailsModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}
    </div>
  );
};

export default Recommendations;
