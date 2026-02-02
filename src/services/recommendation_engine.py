# src/services/recommendation_engine.py
"""
Production-Ready Recommendation Engine
Combines content-based and collaborative filtering with agent memory
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict
import json
import math
from datetime import datetime, timedelta

from src.database.models import (
    Product, User, Wishlist, SearchHistory, 
    ConversationHistory, UserInteraction, Review
)

class ContentBasedFilter:
    """
    Content-Based Filtering: Recommend similar products based on features
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_product_features(self, product: Product) -> Dict:
        """Extract features from a product"""
        return {
            'category': product.category,
            'subcategory': product.subcategory,
            'brand': product.brand,
            'price_range': self._get_price_range(product.price),
            'rating': round(product.rating) if product.rating else 0
        }
    
    def _get_price_range(self, price: float) -> str:
        """Categorize price into ranges"""
        if price < 5000:
            return 'budget'
        elif price < 15000:
            return 'mid_range'
        elif price < 50000:
            return 'premium'
        else:
            return 'luxury'
    
    def calculate_similarity(self, product1: Product, product2: Product) -> float:
        """
        Calculate similarity score between two products (0-1)
        """
        if product1.id == product2.id:
            return 0.0
        
        features1 = self.get_product_features(product1)
        features2 = self.get_product_features(product2)
        
        score = 0.0
        
        # Category match (highest weight)
        if features1['category'] == features2['category']:
            score += 0.4
            
            # Subcategory match (within same category)
            if features1['subcategory'] == features2['subcategory']:
                score += 0.2
        
        # Brand match
        if features1['brand'] == features2['brand']:
            score += 0.15
        
        # Price range match
        if features1['price_range'] == features2['price_range']:
            score += 0.15
        
        # Rating similarity
        rating_diff = abs(features1['rating'] - features2['rating'])
        score += (1 - rating_diff / 5) * 0.1
        
        return min(score, 1.0)
    
    def get_similar_products(
        self, 
        product_id: int, 
        limit: int = 10,
        min_similarity: float = 0.3
    ) -> List[Tuple[Product, float]]:
        """
        Get products similar to the given product
        Returns list of (product, similarity_score) tuples
        """
        base_product = self.db.query(Product).filter(Product.id == product_id).first()
        if not base_product:
            return []
        
        # Get products from same category for efficiency
        candidates = self.db.query(Product).filter(
            Product.category == base_product.category,
            Product.id != product_id,
            Product.in_stock == True
        ).all()
        
        # Calculate similarities
        similarities = []
        for candidate in candidates:
            similarity = self.calculate_similarity(base_product, candidate)
            if similarity >= min_similarity:
                similarities.append((candidate, similarity))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    def recommend_from_wishlist(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Tuple[Product, float]]:
        """
        Recommend products based on user's wishlist
        """
        # Get wishlist products
        wishlist = self.db.query(Wishlist).filter(
            Wishlist.user_id == user_id
        ).all()
        
        if not wishlist:
            return []
        
        # Get similar products for each wishlist item
        all_recommendations = {}
        
        for item in wishlist:
            similar = self.get_similar_products(item.product_id, limit=20)
            for product, score in similar:
                if product.id in all_recommendations:
                    # If already recommended, increase score
                    all_recommendations[product.id] = (
                        product,
                        all_recommendations[product.id][1] + score * 0.5
                    )
                else:
                    all_recommendations[product.id] = (product, score)
        
        # Sort by aggregate score
        recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return recommendations[:limit]


class CollaborativeFilter:
    """
    Collaborative Filtering: Recommend based on similar users' preferences
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_product_matrix(self) -> Dict[int, Dict[int, float]]:
        """
        Build user-product interaction matrix
        Returns: {user_id: {product_id: score}}
        """
        matrix = defaultdict(lambda: defaultdict(float))
        
        # Wishlist interactions (score: 3.0)
        wishlists = self.db.query(Wishlist).all()
        for item in wishlists:
            matrix[item.user_id][item.product_id] += 3.0
        
        # Search history (score: 1.0)
        searches = self.db.query(SearchHistory).filter(
            SearchHistory.clicked_product_id.isnot(None)
        ).all()
        for search in searches:
            if search.user_id and search.clicked_product_id:
                matrix[search.user_id][search.clicked_product_id] += 1.0
        
        # Reviews (score: rating * 0.5)
        reviews = self.db.query(Review).filter(
            Review.user_id.isnot(None)
        ).all()
        for review in reviews:
            if review.user_id:
                matrix[review.user_id][review.product_id] += review.rating * 0.5
        
        return dict(matrix)
    
    def calculate_user_similarity(
        self,
        user1_prefs: Dict[int, float],
        user2_prefs: Dict[int, float]
    ) -> float:
        """
        Calculate cosine similarity between two users
        """
        # Find common products
        common_products = set(user1_prefs.keys()) & set(user2_prefs.keys())
        
        if not common_products:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = sum(
            user1_prefs[p] * user2_prefs[p] 
            for p in common_products
        )
        
        magnitude1 = math.sqrt(sum(v**2 for v in user1_prefs.values()))
        magnitude2 = math.sqrt(sum(v**2 for v in user2_prefs.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def find_similar_users(
        self,
        user_id: int,
        limit: int = 10,
        min_similarity: float = 0.1
    ) -> List[Tuple[int, float]]:
        """
        Find users with similar preferences
        Returns list of (user_id, similarity_score) tuples
        """
        matrix = self.get_user_product_matrix()
        
        if user_id not in matrix:
            return []
        
        user_prefs = matrix[user_id]
        similarities = []
        
        for other_user_id, other_prefs in matrix.items():
            if other_user_id == user_id:
                continue
            
            similarity = self.calculate_user_similarity(user_prefs, other_prefs)
            if similarity >= min_similarity:
                similarities.append((other_user_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    def recommend_from_similar_users(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Tuple[Product, float]]:
        """
        Recommend products based on similar users' preferences
        """
        matrix = self.get_user_product_matrix()
        
        # Find similar users
        similar_users = self.find_similar_users(user_id, limit=20)
        
        if not similar_users:
            return []
        
        # Get current user's products
        user_products = set(matrix.get(user_id, {}).keys())
        
        # Aggregate recommendations from similar users
        recommendations = defaultdict(float)
        
        for similar_user_id, similarity in similar_users:
            similar_user_prefs = matrix.get(similar_user_id, {})
            
            for product_id, score in similar_user_prefs.items():
                # Don't recommend products user already interacted with
                if product_id not in user_products:
                    recommendations[product_id] += score * similarity
        
        # Get product objects and sort
        result = []
        for product_id, score in recommendations.items():
            product = self.db.query(Product).filter(
                Product.id == product_id,
                Product.in_stock == True
            ).first()
            
            if product:
                result.append((product, score))
        
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result[:limit]


class HybridRecommendationEngine:
    """
    Hybrid recommendation system combining multiple strategies with agent memory
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.content_filter = ContentBasedFilter(db)
        self.collab_filter = CollaborativeFilter(db)
    
    def get_agent_memory_context(self, user_id: int) -> Dict:
        """
        Extract context from conversation history for personalized recommendations
        """
        # Get recent conversations
        recent_convs = self.db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id
        ).order_by(
            desc(ConversationHistory.created_at)
        ).limit(10).all()
        
        context = {
            'recent_intents': [],
            'mentioned_products': [],
            'mentioned_categories': [],
            'user_sentiment': 'neutral',
            'price_sensitivity': 'medium'
        }
        
        for conv in recent_convs:
            if conv.intent:
                context['recent_intents'].append(conv.intent)
            
            if conv.products_mentioned:
                try:
                    products = json.loads(conv.products_mentioned)
                    context['mentioned_products'].extend(products)
                except:
                    pass
            
            # Extract categories from messages
            message = conv.user_message.lower()
            categories = ['laptop', 'phone', 'headphone', 'camera', 'watch']
            for cat in categories:
                if cat in message and cat not in context['mentioned_categories']:
                    context['mentioned_categories'].append(cat)
        
        return context
    
    def get_personalized_recommendations(
        self,
        user_id: int,
        limit: int = 20,
        strategy: str = 'hybrid'
    ) -> List[Dict]:
        """
        Get personalized recommendations using hybrid approach
        
        strategy: 'content', 'collaborative', or 'hybrid'
        """
        recommendations = defaultdict(float)
        
        # Get agent memory context
        memory_context = self.get_agent_memory_context(user_id)
        
        if strategy in ['content', 'hybrid']:
            # Content-based from wishlist
            content_recs = self.content_filter.recommend_from_wishlist(user_id, limit=30)
            for product, score in content_recs:
                recommendations[product.id] = (product, recommendations.get(product.id, (product, 0))[1] + score * 0.5)
        
        if strategy in ['collaborative', 'hybrid']:
            # Collaborative filtering
            collab_recs = self.collab_filter.recommend_from_similar_users(user_id, limit=30)
            for product, score in collab_recs:
                recommendations[product.id] = (product, recommendations.get(product.id, (product, 0))[1] + score * 0.5)
        
        # Apply memory-based boosting
        for product_id, (product, score) in list(recommendations.items()):
            # Boost if category mentioned in recent conversations
            if product.category and product.category.lower() in [c.lower() for c in memory_context['mentioned_categories']]:
                recommendations[product_id] = (product, score * 1.3)
            
            # Boost if similar to mentioned products
            if product_id in memory_context['mentioned_products']:
                recommendations[product_id] = (product, score * 1.2)
        
        # Sort by score
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Format response
        result = []
        for product, score in sorted_recs[:limit]:
            result.append({
                'product_id': product.id,
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': float(product.price),
                'rating': float(product.rating) if product.rating else 0.0,
                'image_url': product.image_url,
                'recommendation_score': round(score, 3),
                'in_stock': product.in_stock
            })
        
        return result
    
    def get_trending_products(self, limit: int = 10) -> List[Dict]:
        """
        Get trending products based on recent interactions
        """
        # Products from recent searches (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        trending_searches = self.db.query(
            SearchHistory.clicked_product_id,
            func.count(SearchHistory.id).label('count')
        ).filter(
            SearchHistory.clicked_product_id.isnot(None),
            SearchHistory.search_timestamp >= week_ago
        ).group_by(
            SearchHistory.clicked_product_id
        ).order_by(
            desc('count')
        ).limit(limit).all()
        
        result = []
        for product_id, count in trending_searches:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if product:
                result.append({
                    'product_id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'category': product.category,
                    'price': float(product.price),
                    'rating': float(product.rating) if product.rating else 0.0,
                    'image_url': product.image_url,
                    'trend_score': int(count),
                    'in_stock': product.in_stock
                })
        
        return result
    
    def get_category_recommendations(
        self,
        user_id: int,
        category: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recommendations within a specific category
        """
        # Get user's interaction history
        memory_context = self.get_agent_memory_context(user_id)
        
        # Get products in category
        products = self.db.query(Product).filter(
            Product.category == category,
            Product.in_stock == True
        ).order_by(
            desc(Product.rating)
        ).limit(50).all()
        
        # Score based on rating and user preferences
        scored_products = []
        for product in products:
            score = product.rating if product.rating else 0
            
            # Boost if brand mentioned in conversations
            # (Simplified - in production, use NLP)
            if product.brand and any(
                product.brand.lower() in conv.user_message.lower()
                for conv in self.db.query(ConversationHistory).filter(
                    ConversationHistory.user_id == user_id
                ).limit(20).all()
            ):
                score *= 1.2
            
            scored_products.append((product, score))
        
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        result = []
        for product, score in scored_products[:limit]:
            result.append({
                'product_id': product.id,
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': float(product.price),
                'rating': float(product.rating) if product.rating else 0.0,
                'image_url': product.image_url,
                'recommendation_score': round(score, 2),
                'in_stock': product.in_stock
            })
        
        return result
