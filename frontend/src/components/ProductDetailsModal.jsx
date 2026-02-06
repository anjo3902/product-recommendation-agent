import React from 'react';
import './ProductDetailsModal.css';

/**
 * Product Details Modal Component
 * Beautiful modal to display comprehensive product information
 */
const ProductDetailsModal = ({ product, onClose }) => {
    if (!product) return null;

    const {
        name,
        brand,
        price,
        original_price,
        rating,
        category,
        subcategory,
        description,
        specifications,
        in_stock,
        image_url
    } = product;

    const discount = original_price && price < original_price
        ? Math.round(((original_price - price) / original_price) * 100)
        : null;

    const renderStars = (rating) => {
        const stars = [];
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;

        for (let i = 0; i < fullStars; i++) {
            stars.push(<span key={`full-${i}`} className="star-icon full">★</span>);
        }
        if (hasHalfStar) {
            stars.push(<span key="half" className="star-icon half">★</span>);
        }
        const emptyStars = 5 - Math.ceil(rating);
        for (let i = 0; i < emptyStars; i++) {
            stars.push(<span key={`empty-${i}`} className="star-icon empty">☆</span>);
        }
        return stars;
    };

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

    const getCategoryIcon = () => {
        // Return full category name
        return category || 'Product';
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                {/* Close Button */}
                <button className="modal-close" onClick={onClose}>×</button>

                <div className="modal-body">
                    {/* Left: Image */}
                    <div className="modal-image-section">
                        {image_url ? (
                            <img src={image_url} alt={name} className="modal-product-image" />
                        ) : (
                            <div className="modal-placeholder" style={{ background: getCategoryGradient(category) }}>
                                <div className="placeholder-icon">{getCategoryIcon()}</div>
                                <div className="placeholder-text">{category || 'Product'}</div>
                            </div>
                        )}
                    </div>

                    {/* Right: Details */}
                    <div className="modal-details-section">
                        {/* Category Badge */}
                        <div className="modal-category-badge">
                            {subcategory || category}
                        </div>

                        {/* Product Name */}
                        <h2 className="modal-product-name">{name}</h2>

                        {/* Brand */}
                        <div className="modal-brand">by {brand}</div>

                        {/* Rating */}
                        <div className="modal-rating">
                            <div className="rating-stars">{renderStars(rating)}</div>
                            <span className="rating-value">{rating?.toFixed(1)}</span>
                        </div>

                        {/* Price Section */}
                        <div className="modal-price-section">
                            <div className="modal-price">₹{price?.toLocaleString('en-IN')}</div>
                            {original_price && original_price > price && (
                                <>
                                    <div className="modal-original-price">₹{original_price.toLocaleString('en-IN')}</div>
                                    <div className="modal-discount-badge">-{discount}% OFF</div>
                                </>
                            )}
                        </div>

                        {/* Stock Status */}
                        <div className={`modal-stock ${in_stock ? 'in-stock' : 'out-of-stock'}`}>
                            {in_stock ? 'In Stock' : 'Out of Stock'}
                        </div>

                        {/* Description */}
                        {description && (
                            <div className="modal-section">
                                <h3>Description</h3>
                                <p>{description}</p>
                            </div>
                        )}

                        {/* Specifications */}
                        {specifications && Object.keys(specifications).length > 0 ? (
                            <div className="modal-section">
                                <h3>Detailed Specifications</h3>
                                <div className="specifications-detailed">
                                    {Object.entries(specifications).map(([key, value]) => (
                                        <div key={key} className="spec-row">
                                            <div className="spec-row-label">{key}</div>
                                            <div className="spec-row-value">{value}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="modal-section">
                                <h3>Product Information</h3>
                                <div className="specifications-detailed">
                                    <div className="spec-row">
                                        <div className="spec-row-label">Product Name</div>
                                        <div className="spec-row-value">{name}</div>
                                    </div>
                                    <div className="spec-row">
                                        <div className="spec-row-label">Brand</div>
                                        <div className="spec-row-value">{brand}</div>
                                    </div>
                                    <div className="spec-row">
                                        <div className="spec-row-label">Category</div>
                                        <div className="spec-row-value">{category}</div>
                                    </div>
                                    {subcategory && (
                                        <div className="spec-row">
                                            <div className="spec-row-label">Subcategory</div>
                                            <div className="spec-row-value">{subcategory}</div>
                                        </div>
                                    )}
                                    <div className="spec-row">
                                        <div className="spec-row-label">Price</div>
                                        <div className="spec-row-value">₹{price?.toLocaleString('en-IN')}</div>
                                    </div>
                                    {original_price && original_price > price && (
                                        <div className="spec-row">
                                            <div className="spec-row-label">Original Price</div>
                                            <div className="spec-row-value">₹{original_price.toLocaleString('en-IN')}</div>
                                        </div>
                                    )}
                                    <div className="spec-row">
                                        <div className="spec-row-label">Rating</div>
                                        <div className="spec-row-value">{rating?.toFixed(1)} / 5.0</div>
                                    </div>
                                    <div className="spec-row">
                                        <div className="spec-row-label">Availability</div>
                                        <div className="spec-row-value">{in_stock ? 'In Stock' : 'Out of Stock'}</div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Close Button Only */}
                        <div className="modal-actions">
                            <button className="btn-close-modal" onClick={onClose}>
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductDetailsModal;
