import React from 'react';
import './ProductCard.css';

/**
 * Reusable Product Card Component
 * Production-ready with professional design
 */
const ProductCard = ({
  product,
  onAddToWishlist,
  onViewDetails,
  showSimilar,
  compact = false,
  showRecommendationScore = false
}) => {
  const {
    name,
    brand,
    price,
    original_price,
    rating,
    image_url,
    category,
    subcategory,
    in_stock,
    recommendation_score
  } = product;

  const discount = original_price && price < original_price
    ? Math.round(((original_price - price) / original_price) * 100)
    : null;

  // Get category-specific gradient colors
  const getCategoryGradient = (category) => {
    const cat = category?.toLowerCase() || '';

    // Health & Wellness - Light Green
    if (cat.includes('health') || cat.includes('wellness') || cat.includes('medical') || cat.includes('pharmacy')) {
      return 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)';
    }
    // Pet Supplies - Brown/Orange
    if (cat.includes('pet') || cat.includes('animal')) {
      return 'linear-gradient(135deg, #fdcbf1 0%, #e6dee9 100%)';
    }
    // Baby Products - Soft Pink
    if (cat.includes('baby') || cat.includes('kids') || cat.includes('toys') || cat.includes('children')) {
      return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    }
    // Automotive - Orange/Red
    if (cat.includes('automotive') || cat.includes('car') || cat.includes('bike') || cat.includes('vehicle')) {
      return 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)';
    }
    // Electronics - Blue
    if (cat.includes('laptop') || cat.includes('computer') || cat.includes('electronics')) {
      return 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
    }
    // Mobile/Phone - Purple
    if (cat.includes('phone') || cat.includes('mobile') || cat.includes('smartphone')) {
      return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
    // Audio - Green
    if (cat.includes('headphone') || cat.includes('audio') || cat.includes('speaker') || cat.includes('music')) {
      return 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
    }
    // Camera - Teal
    if (cat.includes('camera') || cat.includes('photo')) {
      return 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)';
    }
    // Watch - Gold
    if (cat.includes('watch') || cat.includes('wearable')) {
      return 'linear-gradient(135deg, #ffd89b 0%, #19547b 100%)';
    }
    // TV - Dark Blue
    if (cat.includes('tv') || cat.includes('television') || cat.includes('display')) {
      return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
    // Home & Kitchen - Warm Orange
    if (cat.includes('home') || cat.includes('kitchen') || cat.includes('furniture')) {
      return 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)';
    }
    // Fashion - Rose
    if (cat.includes('fashion') || cat.includes('clothing') || cat.includes('apparel')) {
      return 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)';
    }
    // Sports - Energetic Red
    if (cat.includes('sport') || cat.includes('fitness') || cat.includes('gym')) {
      return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    }
    // Books - Brown/Beige
    if (cat.includes('book') || cat.includes('education')) {
      return 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)';
    }
    // Beauty & Personal Care - Pink
    if (cat.includes('beauty') || cat.includes('cosmetic') || cat.includes('personal care')) {
      return 'linear-gradient(135deg, #fccb90 0%, #d57eeb 100%)';
    }
    // Office Supplies - Gray/Blue
    if (cat.includes('office') || cat.includes('stationery')) {
      return 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)';
    }
    // Garden & Outdoor - Green
    if (cat.includes('garden') || cat.includes('outdoor') || cat.includes('plant')) {
      return 'linear-gradient(135deg, #96fbc4 0%, #f9f586 100%)';
    }
    // Grocery & Food - Yellow/Orange
    if (cat.includes('grocery') || cat.includes('food') || cat.includes('snack')) {
      return 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)';
    }
    // Default - Purple
    return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={`full-${i}`} className="star full">★</span>);
    }
    if (hasHalfStar) {
      stars.push(<span key="half" className="star half">★</span>);
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="star empty">☆</span>);
    }
    return stars;
  };

  return (
    <div className={`product-card ${compact ? 'compact' : ''} ${!in_stock ? 'out-of-stock' : ''}`}>
      {/* Badges */}
      <div className="product-badges">
        {discount && <span className="badge discount">-{discount}%</span>}
        {!in_stock && <span className="badge out-of-stock-badge">Out of Stock</span>}
        {showRecommendationScore && recommendation_score && (
          <span className="badge recommendation-score">
            {Math.round(recommendation_score * 100)}% Match
          </span>
        )}
      </div>

      {/* Image */}
      <div className="product-image-container">
        {image_url ? (
          <img
            src={image_url}
            alt={name}
            className="product-image"
            loading="lazy"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div
          className="product-placeholder"
          style={{
            display: image_url ? 'none' : 'flex',
            width: '100%',
            height: '100%',
            background: getCategoryGradient(category),
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            color: 'white',
            fontSize: '14px',
            fontWeight: '600',
            textAlign: 'center',
            padding: '20px'
          }}
        >
          <div style={{ fontSize: '48px', marginBottom: '10px' }}>
            {category?.toLowerCase().includes('laptop') ? '💻' :
              category?.toLowerCase().includes('phone') || category?.toLowerCase().includes('mobile') ? '📱' :
                category?.toLowerCase().includes('headphone') || category?.toLowerCase().includes('audio') ? '🎧' :
                  category?.toLowerCase().includes('camera') ? '📷' :
                    category?.toLowerCase().includes('watch') ? '⌚' :
                      category?.toLowerCase().includes('tablet') ? '📱' :
                        category?.toLowerCase().includes('speaker') ? '🔊' :
                          category?.toLowerCase().includes('tv') || category?.toLowerCase().includes('television') ? '📺' :
                            category?.toLowerCase().includes('baby') || category?.toLowerCase().includes('kids') ? '👶' :
                              category?.toLowerCase().includes('automotive') || category?.toLowerCase().includes('car') ? '🚗' :
                                category?.toLowerCase().includes('home') || category?.toLowerCase().includes('kitchen') ? '🏠' :
                                  category?.toLowerCase().includes('fashion') || category?.toLowerCase().includes('clothing') ? '👕' :
                                    category?.toLowerCase().includes('sport') || category?.toLowerCase().includes('fitness') ? '⚽' :
                                      category?.toLowerCase().includes('book') ? '📚' :
                                        '🛍️'}
          </div>
          <div>{category || 'Product'}</div>
        </div>
      </div>

      {/* Content */}
      <div className="product-content">
        <div className="product-category">{subcategory || category}</div>
        <h3 className="product-name">{name}</h3>
        <div className="product-brand">{brand}</div>

        {/* Rating */}
        <div className="product-rating">
          <div className="stars">{renderStars(rating || 0)}</div>
          <span className="rating-value">{rating?.toFixed(1) || 'N/A'}</span>
        </div>

        {/* Price */}
        <div className="product-price-section">
          <div className="product-price">₹{price?.toLocaleString('en-IN')}</div>
          {original_price && original_price > price && (
            <div className="product-original-price">₹{original_price.toLocaleString('en-IN')}</div>
          )}
        </div>

        {/* Actions */}
        <div className="product-actions">
          <button
            className="btn btn-primary"
            onClick={() => onViewDetails && onViewDetails(product)}
            disabled={!in_stock}
          >
            View Details
          </button>
          <button
            className="btn btn-icon"
            onClick={() => onAddToWishlist && onAddToWishlist(product)}
            title="Add to Wishlist"
          >
            ❤️
          </button>
          {showSimilar && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => showSimilar(product)}
            >
              Similar
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
