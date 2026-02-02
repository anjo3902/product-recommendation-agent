"""
Price Tools - Price History Analysis & Deal Detection

This module handles:
1. Fetching price history from database
2. Calculating price trends (increasing/decreasing/stable)
3. Finding products with best discounts
4. Analyzing price statistics

For Beginners:
- "Price History" = how price changed over time (last 30/60/90 days)
- "Trend" = is price going up, down, or staying same?
- "Deal" = product with significant discount from MRP
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.database.models import PriceHistory, Product
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PriceTools:
    """Tools for price tracking and analysis"""
    
    async def get_price_history(
        self,
        db: Session,
        product_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get price history for a product
        
        Args:
            db: Database session
            product_id: Product ID to get history for
            days: Number of days to look back (default: 30)
            
        Returns:
            List of price entries like: [{"price": 2199, "date": "2026-01-01"}, ...]
            
        Example:
            history = await get_price_history(db, product_id=123, days=30)
            # Returns last 30 days of prices
        """
        # Calculate cutoff date (e.g., 30 days ago from today)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query database for price history
        history = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= cutoff_date
        ).order_by(desc(PriceHistory.recorded_at)).all()
        
        # Convert to simple dictionary format
        return [
            {
                "price": float(h.price),
                "date": h.recorded_at.isoformat()  # Convert datetime to string
            }
            for h in history
        ]
    
    async def calculate_price_trend(
        self,
        db: Session,
        product_id: int
    ) -> Dict[str, Any]:
        """
        Calculate price trend analysis
        
        This function analyzes:
        1. Current price vs average price
        2. Is price increasing, decreasing, or stable?
        3. Highest and lowest prices
        4. Should user buy now or wait?
        
        Args:
            db: Database session
            product_id: Product ID to analyze
            
        Returns:
            Dictionary with trend analysis:
            {
                "current_price": 2199,
                "average_price": 2350,
                "min_price": 1999,
                "max_price": 2599,
                "trend": "decreasing",  # or "increasing" or "stable"
                "price_change_pct": -15.4,  # percentage change from highest
                "recommendation": "buy_now",  # or "wait" or "good_time"
                "data_points": 30
            }
        """
        # Get price history for last 30 days
        history = await self.get_price_history(db, product_id, days=30)
        
        if not history:
            return {
                "trend": "unknown",
                "price_change": 0,
                "recommendation": "wait",
                "error": "No price history available"
            }
        
        # Get current product price from products table
        product = db.query(Product).filter(Product.id == product_id).first()
        current_price = float(product.price) if product else 0
        
        # Extract just the price values from history
        prices = [h['price'] for h in history]
        
        # Calculate statistics
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # Determine price trend
        # Compare recent week vs previous week
        if len(prices) >= 14:
            # Last 7 days average
            recent_avg = sum(prices[:7]) / min(7, len(prices))
            
            # Previous 7 days average (days 8-14)
            older_avg = sum(prices[7:14]) / max(1, min(7, len(prices[7:14])))
            
            # If recent average is 5% lower → decreasing
            if recent_avg < older_avg * 0.95:
                trend = "decreasing"
            # If recent average is 5% higher → increasing
            elif recent_avg > older_avg * 1.05:
                trend = "increasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Calculate price change percentage from highest price
        price_change_pct = ((current_price - max_price) / max_price) * 100
        
        # Generate buy/wait recommendation
        if current_price <= min_price * 1.05:  # Within 5% of lowest
            recommendation = "buy_now"
        elif trend == "decreasing":
            recommendation = "wait"  # Prices dropping, wait for lower
        elif current_price >= avg_price:
            recommendation = "wait"  # Above average, not good deal
        else:
            recommendation = "good_time"  # Fair price
        
        # Prepare chart data for frontend visualization
        chart_data = self._prepare_chart_data(history, current_price, avg_price, min_price, max_price)
        
        return {
            "current_price": current_price,
            "average_price": round(avg_price, 2),
            "min_price": min_price,
            "max_price": max_price,
            "trend": trend,
            "price_change_pct": round(price_change_pct, 2),
            "recommendation": recommendation,
            "data_points": len(history),
            "chart_data": chart_data  # Frontend-ready chart format
        }
    
    def _prepare_chart_data(
        self,
        history: List[Dict[str, Any]],
        current_price: float,
        avg_price: float,
        min_price: float,
        max_price: float
    ) -> Dict[str, Any]:
        """
        Prepare price data in chart-ready format for frontend
        
        Returns data structure compatible with Chart.js, Recharts, etc.
        
        Args:
            history: Price history list
            current_price: Current product price
            avg_price: 30-day average price
            min_price: Minimum price in period
            max_price: Maximum price in period
            
        Returns:
            Dictionary with chart-ready data:
            {
                "labels": ["2026-01-01", "2026-01-02", ...],
                "datasets": [
                    {
                        "label": "Price",
                        "data": [2199, 2150, 2100, ...],
                        "borderColor": "#3b82f6",
                        "backgroundColor": "rgba(59, 130, 246, 0.1)"
                    },
                    {
                        "label": "Average Price",
                        "data": [2350, 2350, ...],  # Horizontal line
                        "borderColor": "#10b981",
                        "borderDash": [5, 5]  # Dashed line
                    }
                ],
                "markers": {
                    "current": current_price,
                    "lowest": min_price,
                    "highest": max_price
                }
            }
        """
        # Sort history by date (oldest to newest for chart)
        sorted_history = sorted(history, key=lambda x: x['date'])
        
        # Extract labels (dates) and data (prices)
        labels = [h['date'][:10] for h in sorted_history]  # Format: YYYY-MM-DD
        prices = [h['price'] for h in sorted_history]
        
        # Create average price line (constant across all dates)
        avg_line = [avg_price] * len(labels)
        
        # Prepare Chart.js compatible structure
        chart_data = {
            "type": "line",  # Chart type
            "labels": labels,
            "datasets": [
                {
                    "label": "Price History",
                    "data": prices,
                    "borderColor": "#3b82f6",  # Blue
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "borderWidth": 2,
                    "fill": True,
                    "tension": 0.4  # Smooth curve
                },
                {
                    "label": "30-Day Average",
                    "data": avg_line,
                    "borderColor": "#10b981",  # Green
                    "borderWidth": 2,
                    "borderDash": [5, 5],  # Dashed line
                    "fill": False,
                    "pointRadius": 0  # No points on average line
                }
            ],
            "markers": {
                "current_price": {
                    "value": current_price,
                    "color": "#ef4444",  # Red
                    "label": "Current"
                },
                "lowest_price": {
                    "value": min_price,
                    "color": "#22c55e",  # Green
                    "label": "Lowest"
                },
                "highest_price": {
                    "value": max_price,
                    "color": "#f59e0b",  # Orange
                    "label": "Highest"
                }
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": False,
                        "title": {
                            "display": True,
                            "text": "Price (₹)"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Date"
                        }
                    }
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "30-Day Price Trend"
                    },
                    "legend": {
                        "display": True,
                        "position": "top"
                    }
                }
            }
        }
        
        return chart_data
    
    async def find_deals(
        self,
        db: Session,
        category: str = None,
        min_discount: float = 10.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find products with significant discounts
        
        A "deal" is when current price is much lower than MRP (Maximum Retail Price)
        
        Args:
            db: Database session
            category: Filter by category (optional)
            min_discount: Minimum discount percentage (default: 10%)
            limit: Maximum number of deals to return
            
        Returns:
            List of deals sorted by discount percentage (highest first)
            
        Example:
            deals = await find_deals(db, category="Electronics", min_discount=20)
            # Returns: Electronics products with 20%+ discount
        """
        # Start building query
        query = db.query(Product).filter(
            Product.mrp.isnot(None),  # Must have MRP
            Product.in_stock == True   # Must be in stock
        )
        
        # Filter by category if provided
        if category:
            query = query.filter(Product.category == category)
        
        # Get all matching products
        products = query.limit(limit * 2).all()  # Get extra for filtering
        
        deals = []
        for product in products:
            if product.mrp and product.price:
                # Calculate discount percentage
                # Formula: ((MRP - Price) / MRP) * 100
                discount_pct = ((product.mrp - product.price) / product.mrp) * 100
                
                # Only include if discount meets minimum threshold
                if discount_pct >= min_discount:
                    # Check if this is a flash deal (price dropped recently)
                    is_flash = await self._is_flash_deal(db, product.id)
                    
                    deals.append({
                        "product_id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "category": product.category,
                        "price": float(product.price),
                        "mrp": float(product.mrp),
                        "discount_pct": round(discount_pct, 2),
                        "savings": round(product.mrp - product.price, 2),
                        "rating": float(product.rating),
                        "review_count": product.review_count,
                        "is_flash_deal": is_flash,  # NEW: Flash deal indicator
                        "deal_type": "flash" if is_flash else "regular"  # NEW: Deal type
                    })
        
        # Sort by discount percentage (highest discount first)
        deals.sort(key=lambda x: x['discount_pct'], reverse=True)
        
        return deals[:limit]  # Return only requested number
    
    async def _is_flash_deal(
        self,
        db: Session,
        product_id: int
    ) -> bool:
        """
        Detect if product is a flash/blast deal
        
        A flash deal is when:
        1. Price dropped significantly (>10%) in last 48 hours
        2. OR price is at all-time low in last 90 days
        
        Args:
            db: Database session
            product_id: Product ID
            
        Returns:
            True if flash deal, False otherwise
        """
        try:
            # Get recent price history (last 7 days)
            recent_history = await self.get_price_history(db, product_id, days=7)
            
            if len(recent_history) < 2:
                return False
            
            # Current price
            current_price = recent_history[0]['price']
            
            # Price 2 days ago
            if len(recent_history) >= 3:
                old_price = recent_history[2]['price']
                
                # Calculate price drop
                price_drop_pct = ((old_price - current_price) / old_price) * 100
                
                # Flash deal if dropped >10% in last 48 hours
                if price_drop_pct >= 10:
                    return True
            
            # Check if at all-time low (last 90 days)
            full_history = await self.get_price_history(db, product_id, days=90)
            
            if full_history:
                all_prices = [h['price'] for h in full_history]
                min_price = min(all_prices)
                
                # Flash deal if current price is lowest in 90 days
                if current_price <= min_price * 1.01:  # Within 1% of lowest
                    return True
            
            return False
            
        except Exception as e:
            # If error, not a flash deal
            return False
    
    async def find_flash_deals(
        self,
        db: Session,
        category: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find ONLY flash/blast deals
        
        Flash deals are urgent deals that users should act on quickly:
        - Price dropped >10% in last 48 hours
        - OR price at all-time low
        
        Args:
            db: Database session
            category: Filter by category (optional)
            limit: Maximum number of flash deals
            
        Returns:
            List of flash deals with urgency indicators
        """
        # Get all deals
        all_deals = await self.find_deals(db, category, min_discount=10.0, limit=limit * 3)
        
        # Filter only flash deals
        flash_deals = [deal for deal in all_deals if deal.get('is_flash_deal')]
        
        # Add urgency score
        for deal in flash_deals:
            # Higher urgency = higher discount + flash status
            urgency_score = deal['discount_pct']
            
            if deal['discount_pct'] >= 40:
                urgency_level = "extreme"  # 40%+ discount
            elif deal['discount_pct'] >= 25:
                urgency_level = "high"     # 25-40% discount
            elif deal['discount_pct'] >= 15:
                urgency_level = "medium"   # 15-25% discount
            else:
                urgency_level = "low"      # 10-15% discount
            
            deal['urgency_level'] = urgency_level
            deal['urgency_score'] = round(urgency_score, 2)
        
        # Sort by urgency (highest first)
        flash_deals.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return flash_deals[:limit]


# Global instance for easy importing
price_tools = PriceTools()
