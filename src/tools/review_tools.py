# src/tools/review_tools.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models import Review
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ReviewTools:
    """Tools for review analysis"""
    
    async def get_reviews(
        self,
        db: Session,
        product_id: int,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get reviews for a product
        
        Args:
            db: Database session
            product_id: Product ID
            limit: Maximum reviews to fetch
            
        Returns:
            List of review dictionaries
        """
        reviews = db.query(Review).filter(
            Review.product_id == product_id
        ).order_by(
            Review.helpful_count.desc()
        ).limit(limit).all()
        
        return [
            {
                "rating": r.rating,
                "text": r.review_text,
                "verified": r.verified_purchase,
                "helpful_count": r.helpful_count
            }
            for r in reviews
        ]
    
    async def get_review_statistics(
        self,
        db: Session,
        product_id: int
    ) -> Dict:
        """
        Calculate review statistics
        
        Args:
            db: Database session
            product_id: Product ID
            
        Returns:
            Statistics dictionary
        """
        # Get all reviews
        reviews = db.query(Review).filter(
            Review.product_id == product_id
        ).all()
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "rating_distribution_pct": {},
                "verified_purchases": 0
            }
        
        # Calculate statistics
        total = len(reviews)
        avg_rating = sum(r.rating for r in reviews) / total
        
        # Rating distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in reviews:
            distribution[r.rating] = distribution.get(r.rating, 0) + 1
        
        # Convert to percentages
        distribution_pct = {
            rating: (count / total) * 100
            for rating, count in distribution.items()
        }
        
        return {
            "total_reviews": total,
            "average_rating": round(avg_rating, 2),
            "rating_distribution": distribution,
            "rating_distribution_pct": distribution_pct,
            "verified_purchases": sum(1 for r in reviews if r.verified_purchase)
        }
    
    async def extract_themes(
        self,
        reviews: List[Dict],
        min_mentions: int = 3
    ) -> Dict[str, List[str]]:
        """
        Extract common themes from reviews (simple keyword-based)
        
        Args:
            reviews: List of reviews
            min_mentions: Minimum times a theme must appear
            
        Returns:
            Dictionary of positive and negative themes
        """
        # Common positive/negative keywords
        positive_keywords = {
            'excellent', 'great', 'amazing', 'good', 'best', 'love',
            'perfect', 'fantastic', 'awesome', 'quality', 'worth',
            'comfortable', 'easy', 'fast', 'clear', 'bright', 'beautiful',
            'sturdy', 'reliable', 'durable', 'impressive', 'satisfied',
            'recommend', 'happy', 'pleased', 'outstanding', 'superb'
        }
        
        negative_keywords = {
            'bad', 'poor', 'terrible', 'worst', 'hate', 'issue',
            'problem', 'broken', 'defective', 'disappointed', 'waste',
            'cheap', 'slow', 'difficult', 'uncomfortable', 'useless',
            'failed', 'not working', 'stopped', 'damage', 'faulty'
        }
        
        positive_themes = []
        negative_themes = []
        
        for review in reviews:
            text = review['text'].lower() if review['text'] else ""
            
            # Find positive themes
            for keyword in positive_keywords:
                if keyword in text:
                    # Extract context (5 words around keyword)
                    words = text.split()
                    for i, word in enumerate(words):
                        if keyword in word:
                            context_start = max(0, i - 2)
                            context_end = min(len(words), i + 3)
                            context = ' '.join(words[context_start:context_end])
                            positive_themes.append(context)
            
            # Find negative themes
            for keyword in negative_keywords:
                if keyword in text:
                    words = text.split()
                    for i, word in enumerate(words):
                        if keyword in word:
                            context_start = max(0, i - 2)
                            context_end = min(len(words), i + 3)
                            context = ' '.join(words[context_start:context_end])
                            negative_themes.append(context)
        
        return {
            "positive": positive_themes[:10],  # Top 10
            "negative": negative_themes[:10]
        }

# Global instance
review_tools = ReviewTools()
