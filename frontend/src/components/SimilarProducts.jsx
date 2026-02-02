import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import './SimilarProducts.css';

/**
 * Similar Products Widget Component
 * Production-ready widget for showing similar products
 */
const SimilarProducts = ({ productId, productName }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [error, setError] = useState('');
  const [limit, setLimit] = useState(6);

  useEffect(() => {
    if (productId) {
      fetchSimilarProducts();
    }
  }, [productId, limit]);

  const fetchSimilarProducts = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(
        `http://localhost:8000/recommendations/similar/${productId}?limit=${limit}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch similar products');
      }

      const data = await response.json();
      setSimilarProducts(data.similar_products || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching similar products:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToWishlist = async (product) => {
    try {
      const response = await fetch('http://localhost:8000/preferences/wishlist', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
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
    console.log('View product:', product);
    alert(`Product Details: ${product.name}\nPrice: $${product.price}\nRating: ${product.rating}`);
  };

  if (loading) {
    return (
      <div className="similar-products-widget">
        <div className="widget-header">
          <h3>🔗 Similar Products</h3>
        </div>
        <div className="widget-loading">
          <div className="spinner"></div>
          <p>Finding similar products...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="similar-products-widget">
        <div className="widget-header">
          <h3>🔗 Similar Products</h3>
        </div>
        <div className="widget-error">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button className="btn-retry" onClick={fetchSimilarProducts}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (similarProducts.length === 0) {
    return (
      <div className="similar-products-widget">
        <div className="widget-header">
          <h3>🔗 Similar Products</h3>
        </div>
        <div className="widget-empty">
          <p>No similar products found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="similar-products-widget">
      <div className="widget-header">
        <div>
          <h3>🔗 Similar Products</h3>
          {productName && <p className="widget-subtitle">Similar to "{productName}"</p>}
        </div>
        <select 
          value={limit} 
          onChange={(e) => setLimit(parseInt(e.target.value))}
          className="limit-select"
        >
          <option value="3">3 items</option>
          <option value="6">6 items</option>
          <option value="12">12 items</option>
        </select>
      </div>

      <div className="similar-products-carousel">
        {Array.isArray(similarProducts) && similarProducts.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToWishlist={handleAddToWishlist}
            onViewDetails={handleViewDetails}
            compact={true}
            showRecommendationScore={true}
          />
        ))}
      </div>

      {similarProducts.length > 0 && (
        <div className="widget-footer">
          <p>Showing {similarProducts.length} similar items based on category, brand, and price</p>
        </div>
      )}
    </div>
  );
};

export default SimilarProducts;
