import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import ProductDetailsModal from './ProductDetailsModal';
import API_BASE_URL from '../config';
import './Recommendations.css';

/**
 * Recommendations Display Component - Amazon/Flipkart Style
 * Automatic personalized recommendations without user configuration
 */
const Recommendations = ({ isActive = true }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [toast, setToast] = useState(null);

  // Auto-dismiss toast after 3 seconds
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  // Lazy load - only fetch when page becomes active for the first time
  useEffect(() => {
    if (isActive && !hasLoaded) {
      fetchRecommendations(); // First load with spinner
      setHasLoaded(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive]);

  // Listen for wishlist changes from other components
  useEffect(() => {
    const handleWishlistChange = () => {
      if (hasLoaded && recommendations.length > 0) {
        fetchRecommendations(true); // Silent refresh without loading spinner
      }
    };

    window.addEventListener('wishlistChanged', handleWishlistChange);
    return () => window.removeEventListener('wishlistChanged', handleWishlistChange);
  }, [hasLoaded, recommendations.length]);

  const fetchRecommendations = async (silent = false) => {
    try {
      // Only show loading on very first load, then always update silently
      if (!silent && !hasLoaded) {
        setLoading(true);
      }
      setError('');

      // Use hybrid strategy by default (best results like Amazon/Flipkart)
      const url = `${API_BASE_URL}/recommendations/personalized?strategy=hybrid&limit=50`;

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
      if (!silent && !hasLoaded) {
        setError(err.message);
      }
      console.error('Error fetching recommendations:', err);
    } finally {
      if (!silent && !hasLoaded) {
        setLoading(false);
      }
    }
  };

  const handleAddToWishlist = (product) => {
    // API returns 'product_id', not 'id'
    const productId = product.product_id || product.id;

    if (!productId) {
      showToast('Error: Product ID not found', 'error');
      console.error('Product object:', product);
      return;
    }

    // Show immediate feedback - optimistic UI
    showToast('Adding to wishlist...', 'success');

    // Fire-and-forget: Send request in background without blocking
    fetch(`${API_BASE_URL}/preferences/wishlist`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ product_id: productId }),
    })
      .then(response => {
        if (response.ok) {
          showToast('Added to wishlist!', 'success');
          // Notify other components about wishlist change
          window.dispatchEvent(new Event('wishlistChanged'));
        } else {
          return response.json().then(errorData => {
            if (response.status === 400 && errorData.detail?.includes('already in wishlist')) {
              showToast('Already in your wishlist', 'info');
            } else {
              showToast(`Failed: ${errorData.detail || 'Unknown error'}`, 'error');
            }
          });
        }
      })
      .catch(err => {
        console.error('Error adding to wishlist:', err);
        showToast('Network error', 'error');
      });
  };

  const handleViewDetails = (product) => {
    console.log('View product:', product);
    setSelectedProduct(product);
  };

  return (
    <div className="recommendations-container">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          <span>{toast.message}</span>
          <button onClick={() => setToast(null)}>&times;</button>
        </div>
      )}

      {/* Simple Header - Like Amazon */}
      <div className="recommendations-header-simple">
        <h1>Recommended for you</h1>
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
          <span className="error-icon">!</span>
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
              <div className="empty-icon">!</div>
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
