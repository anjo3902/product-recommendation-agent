# src/routes/recommendations.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.database.connection import get_db
from src.database.models import User
from src.utils.middleware import get_current_user
from src.services.recommendation_engine import HybridRecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/personalized")
async def get_personalized_recommendations(
    limit: int = Query(20, ge=1, le=100),
    strategy: str = Query('hybrid', regex='^(content|collaborative|hybrid)$'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized product recommendations for the current user.
    
    Uses hybrid recommendation engine combining:
    - Content-based filtering (similar products)
    - Collaborative filtering (similar users)
    - Agent memory (conversation history)
    
    **Parameters:**
    - **limit**: Number of recommendations (1-100)
    - **strategy**: Recommendation strategy
      - `content`: Content-based filtering only
      - `collaborative`: Collaborative filtering only
      - `hybrid`: Combined approach (recommended)
    
    **Returns:** List of recommended products with scores
    """
    engine = HybridRecommendationEngine(db)
    recommendations = engine.get_personalized_recommendations(
        user_id=current_user.id,
        limit=limit,
        strategy=strategy
    )
    
    return {
        "user_id": current_user.id,
        "strategy": strategy,
        "count": len(recommendations),
        "recommendations": recommendations
    }

@router.get("/trending")
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get trending products based on recent user interactions.
    
    Products are ranked by:
    - Recent search clicks
    - Wishlist additions
    - View counts
    
    **Parameters:**
    - **limit**: Number of trending products (1-50)
    """
    engine = HybridRecommendationEngine(db)
    trending = engine.get_trending_products(limit=limit)
    
    return {
        "count": len(trending),
        "trending_products": trending
    }

@router.get("/category/{category}")
async def get_category_recommendations(
    category: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized recommendations within a specific category.
    
    Considers user's conversation history and preferences
    for the given category.
    
    **Parameters:**
    - **category**: Product category
    - **limit**: Number of recommendations (1-50)
    """
    engine = HybridRecommendationEngine(db)
    recommendations = engine.get_category_recommendations(
        user_id=current_user.id,
        category=category,
        limit=limit
    )
    
    return {
        "user_id": current_user.id,
        "category": category,
        "count": len(recommendations),
        "recommendations": recommendations
    }

@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get products similar to a specific product.
    
    Uses content-based filtering to find products with similar:
    - Category
    - Brand
    - Price range
    - Features
    
    **Parameters:**
    - **product_id**: ID of the base product
    - **limit**: Number of similar products (1-50)
    """
    engine = HybridRecommendationEngine(db)
    similar_products = engine.content_filter.get_similar_products(
        product_id=product_id,
        limit=limit
    )
    
    result = []
    for product, similarity_score in similar_products:
        result.append({
            'product_id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category,
            'price': float(product.price),
            'rating': float(product.rating) if product.rating else 0.0,
            'image_url': product.image_url,
            'similarity_score': round(similarity_score, 3),
            'in_stock': product.in_stock
        })
    
    return {
        "base_product_id": product_id,
        "count": len(result),
        "similar_products": result
    }

@router.get("/for-you")
async def get_for_you_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive "For You" recommendations.
    
    Combines multiple recommendation strategies:
    - Personalized hybrid recommendations
    - Trending products
    - Category-specific recommendations
    
    **Returns:** Curated collection of recommendations
    """
    engine = HybridRecommendationEngine(db)
    
    # Get personalized recommendations
    personalized = engine.get_personalized_recommendations(
        user_id=current_user.id,
        limit=15,
        strategy='hybrid'
    )
    
    # Get trending products
    trending = engine.get_trending_products(limit=10)
    
    # Get memory context for category suggestions
    memory_context = engine.get_agent_memory_context(current_user.id)
    
    category_recommendations = {}
    for category in memory_context['mentioned_categories'][:3]:
        cat_recs = engine.get_category_recommendations(
            user_id=current_user.id,
            category=category,
            limit=5
        )
        if cat_recs:
            category_recommendations[category] = cat_recs
    
    return {
        "user_id": current_user.id,
        "personalized_recommendations": {
            "count": len(personalized),
            "products": personalized
        },
        "trending": {
            "count": len(trending),
            "products": trending
        },
        "category_recommendations": category_recommendations,
        "user_insights": {
            "recent_interests": memory_context['mentioned_categories'],
            "recent_intents": memory_context['recent_intents'][:5]
        }
    }

@router.get("/insights")
async def get_recommendation_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get insights about recommendation factors for the user.
    
    Helps understand why certain products are recommended.
    """
    engine = HybridRecommendationEngine(db)
    
    # Get agent memory
    memory_context = engine.get_agent_memory_context(current_user.id)
    
    # Get similar users
    similar_users = engine.collab_filter.find_similar_users(
        user_id=current_user.id,
        limit=5
    )
    
    return {
        "user_id": current_user.id,
        "memory_context": {
            "recent_intents": memory_context['recent_intents'],
            "mentioned_categories": memory_context['mentioned_categories'],
            "mentioned_products": memory_context['mentioned_products']
        },
        "similar_users_count": len(similar_users),
        "recommendation_factors": {
            "conversation_history": "Recent conversations influence recommendations",
            "wishlist_items": "Products in wishlist guide similar product suggestions",
            "search_history": "Past searches help identify preferences",
            "similar_users": "Recommendations based on users with similar tastes"
        }
    }
