// frontend/src/components/Wishlist.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ProductCard from './ProductCard';
import ProductDetailsModal from './ProductDetailsModal';
import API_BASE_URL from '../config';
import './Wishlist.css';

const Wishlist = () => {
  const { token } = useAuth();
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingNote, setEditingNote] = useState(null);
  const [noteText, setNoteText] = useState('');
  const [stats, setStats] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);



  // Fetch wishlist items
  useEffect(() => {
    fetchWishlist();
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchWishlist = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${API_BASE_URL}/preferences/wishlist`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch wishlist');
      }

      const data = await response.json();
      setWishlistItems(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching wishlist:', err);
    } finally {
      setLoading(false);
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

    try {
      const response = await fetch(`${API_BASE_URL}/preferences/wishlist/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove item');
      }

      // Update UI
      setWishlistItems(wishlistItems.filter(item => item.id !== itemId));
      fetchStats(); // Refresh stats
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
  const mapItemToProduct = (item) => ({
    id: item.product_id || item.id,
    name: item.product_name,
    brand: item.brand || 'Brand', // Fallback if missing
    price: item.product_price,
    original_price: item.original_price,
    rating: item.product_rating,
    image_url: item.product_image,
    category: item.category,
    subcategory: item.subcategory,
    description: item.description,
    specifications: item.specifications,
    in_stock: item.in_stock !== false // Default to true if missing
  });

  // ... (keep handleRemoveItem, handleEditNote, etc.)

  // Note: I will need to make sure handleRemoveItem is passed correctly.

  return (
    <div className="wishlist-container">
      <div className="wishlist-header">
        <h1>My Wishlist</h1>
        {stats && (
          <div className="wishlist-stats">
            <div className="stat-item">
              <span className="stat-value">{stats.wishlist_count}</span>
              <span className="stat-label">Items</span>
            </div>
            {stats.favorite_categories.length > 0 && (
              <div className="stat-item">
                <span className="stat-value">{stats.favorite_categories[0]}</span>
                <span className="stat-label">Top Category</span>
              </div>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {wishlistItems.length === 0 ? (
        <div className="empty-wishlist">
          <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <h2>Your wishlist is empty</h2>
          <p>Start adding products you love!</p>
        </div>
      ) : (
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
      )}

      {stats && stats.favorite_categories.length > 0 && (
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
