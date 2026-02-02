# src/database/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)  # Primary key automatically indexed
    name = Column(String(500), nullable=False, index=True)  # Index for text search
    brand = Column(String(200), index=True)  # Index for brand filtering
    model = Column(String(200))
    category = Column(String(100), nullable=False, index=True)  # Index for category filtering
    subcategory = Column(String(100), index=True)  # Index for subcategory filtering
    price = Column(Float, nullable=False, index=True)  # Index for price range queries
    mrp = Column(Float)
    description = Column(Text)
    features = Column(Text)  # JSON string of features
    specifications = Column(Text)  # JSON string of specifications
    rating = Column(Float, default=0.0, index=True)  # Index for rating filtering
    review_count = Column(Integer, default=0, index=True)  # Index for popularity sorting
    image_url = Column(String(500))
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    card_offers = relationship("CardOffer", back_populates="product", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "model": self.model,
            "category": self.category,
            "subcategory": self.subcategory,
            "price": float(self.price),
            "mrp": float(self.mrp) if self.mrp else None,
            "description": self.description,
            "features": self.features,
            "specifications": self.specifications,
            "rating": float(self.rating) if self.rating else 0.0,
            "review_count": self.review_count,
            "image_url": self.image_url,
            "in_stock": self.in_stock,
            "stock_quantity": self.stock_quantity
        }

class Review(Base):
    """Review model"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)  # Critical index for JOIN queries
    user_id = Column(Integer, index=True)  # Index for user review lookups
    rating = Column(Integer, nullable=False, index=True)  # Index for rating filtering
    review_text = Column(Text)
    helpful_count = Column(Integer, default=0)
    verified_purchase = Column(Boolean, default=False, index=True)  # Index for verified filtering
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="reviews")

class PriceHistory(Base):
    """Price history model"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)  # Critical index for product price history
    price = Column(Float, nullable=False, index=True)  # Index for price queries
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)  # Index for date range queries
    
    product = relationship("Product", back_populates="price_history")

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class ProductFeature(Base):
    """Product features model - Optional table for structured feature storage"""
    __tablename__ = "product_features"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    feature_name = Column(String(200))
    feature_value = Column(String(500))
    feature_category = Column(String(100))
    
    # Note: Not used by data generation script (uses Product.features JSON field instead)

class CardOffer(Base):
    """Card offers model"""
    __tablename__ = "card_offers"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    bank_name = Column(String(100), nullable=False)
    card_type = Column(String(50))
    offer_type = Column(String(50))
    discount_amount = Column(Float)
    discount_percentage = Column(Float)
    cashback_amount = Column(Float)
    min_transaction_amount = Column(Float)
    emi_tenure = Column(String(50))
    is_no_cost_emi = Column(Boolean, default=False)
    offer_description = Column(Text)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime)
    valid_till = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="card_offers")

class ShoppingCart(Base):
    """Shopping cart model"""
    __tablename__ = "shopping_cart"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, default=datetime.utcnow)

class Wishlist(Base):
    """Wishlist model"""
    __tablename__ = "wishlist"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    notes = Column(Text)
    added_at = Column(DateTime, default=datetime.utcnow)

class SearchHistory(Base):
    """Search history model"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(Text, nullable=False)
    results_count = Column(Integer)
    clicked_product_id = Column(Integer)
    search_timestamp = Column(DateTime, default=datetime.utcnow)

class ConversationHistory(Base):
    """Conversation history model for agent memory"""
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100))  # Group related conversations
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    context_data = Column(Text)  # JSON string with additional context
    products_mentioned = Column(Text)  # JSON array of product IDs
    intent = Column(String(50))  # search, compare, buy_plan, etc.
    sentiment = Column(String(20))  # positive, neutral, negative
    created_at = Column(DateTime, default=datetime.utcnow)

class UserInteraction(Base):
    """User interaction model for collaborative filtering"""
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # view, wishlist, purchase, rating
    interaction_value = Column(Float)  # rating score, time spent, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    """Notifications model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    notification_type = Column(String(50))
    title = Column(String(255))
    message = Column(Text)
    priority = Column(String(20), default="normal")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
