// frontend/src/components/Wishlist.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import ProductDetailsModal from './ProductDetailsModal';
import API_BASE_URL from '../config';
import { getApiHeaders } from '../utils/api';
import './Wishlist.css';

const Wishlist = ({ isActive = true }) => {
  const { token } = useAuth();
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingNote, setEditingNote] = useState(null);
  const [noteText, setNoteText] = useState('');
  const [stats, setStats] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [hasLoaded, setHasLoaded] = useState(false);

  // Lazy load - only fetch when page becomes active for the first time
  useEffect(() => {
    if (isActive && !hasLoaded && token) {
      setHasLoaded(true);
      fetchWishlist();
      fetchStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive, token]);

  // Listen for wishlist changes from other components
  useEffect(() => {
    const handleWishlistChange = () => {
      if (hasLoaded) {
        fetchWishlist(true); // Silent refresh without loading spinner
        fetchStats();
      }
    };

    window.addEventListener('wishlistChanged', handleWishlistChange);
    return () => window.removeEventListener('wishlistChanged', handleWishlistChange);
  }, [hasLoaded]);

  const fetchWishlist = async (silent = false) => {
    if (!token) {
      setError('Please log in to view your wishlist');
      return;
    }

    try {
      if (!silent) {
        setLoading(true);
      }
      setError('');

      const response = await fetch(`${API_BASE_URL}/preferences/wishlist`, {
        method: 'GET',
        headers: getApiHeaders(token)
      });

      if (!response.ok) {
        throw new Error('Failed to fetch wishlist');
      }

      const data = await response.json();
      setWishlistItems(data);
    } catch (err) {
      if (!silent) {
        setError(err.message);
      }
      console.error('Error fetching wishlist:', err);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/preferences/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!window.confirm('Remove this item from wishlist?')) {
      return;
    }

    // Optimistic UI update - remove immediately for smooth experience
    const itemToRemove = wishlistItems.find(item => item.id === itemId);
    setWishlistItems(wishlistItems.filter(item => item.id !== itemId));

    try {
      const response = await fetch(`${API_BASE_URL}/preferences/wishlist/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        // Revert on error
        setWishlistItems(prev => [...prev, itemToRemove]);
        throw new Error('Failed to remove item');
      }

      // Refresh stats after successful removal
      fetchStats();
      
      // Notify other components about wishlist change
      window.dispatchEvent(new Event('wishlistChanged'));
    } catch (err) {
      setError(err.message);
      console.error('Error removing item:', err);
    }
  };

  const handleEditNote = (item) => {
    setEditingNote(item.id);
    setNoteText(item.notes || '');
  };

  const handleSaveNote = async (itemId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/preferences/wishlist/${itemId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: noteText })
      });

      if (!response.ok) {
        throw new Error('Failed to update note');
      }

      // Update UI
      setWishlistItems(wishlistItems.map(item =>
        item.id === itemId ? { ...item, notes: noteText } : item
      ));
      setEditingNote(null);
      setNoteText('');
    } catch (err) {
      setError(err.message);
      console.error('Error updating note:', err);
    }
  };





  if (loading) {
    return (
      <div className="wishlist-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading wishlist...</p>
        </div>
      </div>
    );
  }

  // Helper to map wishlist item to product structure
  const mapItemToProduct = (item) => {
    // Debug log to see what data we're getting
    if (!item.category) {
      console.log('Wishlist item missing category:', item);
    }
    
    return {
      id: item.product_id || item.id,
      name: item.product_name || item.name,
      brand: item.brand || 'Brand',
      price: item.product_price || item.price,
      original_price: item.original_price,
      rating: item.product_rating || item.rating,
      image_url: item.product_image || item.image_url,
      category: item.category || 'Product',
      subcategory: item.subcategory || item.product_subcategory,
      description: item.description,
      specifications: item.specifications,
      in_stock: item.in_stock !== false
    };
  };

  // ... (keep handleRemoveItem, handleEditNote, etc.)

  // Note: I will need to make sure handleRemoveItem is passed correctly.

  return (
    <div className="wishlist-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1>My Wishlist</h1>
          <p>Your collection of favorite products</p>
        </div>
        {stats && (
          <div className="insights-card">
            <h3>Quick Stats</h3>
            <div className="insights-grid">
              <div className="insight-item">
                <div className="insight-value">{stats.wishlist_count}</div>
                <div className="insight-label">Saved Items</div>
              </div>
              {stats.favorite_categories.length > 0 && (
                <div className="insight-item">
                  <div className="insight-value">{stats.favorite_categories[0]}</div>
                  <div className="insight-label">Top Category</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {wishlistItems.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon-wrapper">
            <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <h2>Your wishlist is empty</h2>
          <p>Start adding products you love to see them here!</p>
        </div>
      ) : (
        <div className="wishlist-section">
        <div className="wishlist-grid">
          {wishlistItems.map(item => {
            const product = mapItemToProduct(item);
            return (
              <div key={item.id} className="wishlist-card-wrapper">
                <ProductCard
                  product={product}
                  onViewDetails={() => setSelectedProduct(product)}
                  onAddToWishlist={() => handleRemoveItem(item.id)}
                  isWishlisted={true}
                />

                <div className="wishlist-item-footer">
                  <div className="added-date">
                    Added on {new Date(item.added_at).toLocaleDateString()}
                  </div>

                  {editingNote === item.id ? (
                    <div className="note-edit">
                      <textarea
                        value={noteText}
                        onChange={(e) => setNoteText(e.target.value)}
                        placeholder="Add notes about this product..."
                        rows="3"
                      />
                      <div className="note-actions">
                        <button
                          className="btn-save"
                          onClick={() => handleSaveNote(item.id)}
                        >
                          Save
                        </button>
                        <button
                          className="btn-cancel"
                          onClick={() => {
                            setEditingNote(null);
                            setNoteText('');
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="notes-section">
                      {item.notes ? (
                        <div className="note-display">
                          <p>{item.notes}</p>
                          <button
                            className="btn-edit-note"
                            onClick={() => handleEditNote(item)}
                          >
                            Edit Note
                          </button>
                        </div>
                      ) : (
                        <button
                          className="btn-add-note"
                          onClick={() => handleEditNote(item)}
                        >
                          + Add Note
                        </button>
                      )}
                    </div>
                  )}

                  <button
                    className="btn-remove-text"
                    onClick={() => handleRemoveItem(item.id)}
                  >
                    Remove from Wishlist
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        </div>
      )}

      {stats && stats.favorite_categories.length > 0 && wishlistItems.length > 0 && (
        <div className="favorite-categories">
          <h3>Your Favorite Categories</h3>
          <div className="category-tags">
            {stats.favorite_categories.map((category, index) => (
              <span key={index} className="category-tag">
                {category}
              </span>
            ))}
          </div>
        </div>
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

export default Wishlist;
