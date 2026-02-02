"""
Price Tracker Agent - AI-Powered Price Analysis

This agent uses Ollama AI to:
1. Analyze price trends and patterns
2. Recommend buy/wait decisions
3. Explain reasoning in human language
4. Find best deals across products

For Beginners:
- This is like a smart shopping assistant
- It looks at price history and tells you "Buy now!" or "Wait for better deal"
- Uses AI to explain WHY in simple terms
"""

import ollama
import asyncio
from src.tools.price_tools import price_tools
from src.database.connection import get_db
from src.database.models import Product
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class PriceTrackerAgent:
    """AI-powered price tracking and recommendation agent"""
    
    def __init__(self):
        """Initialize the agent with Ollama"""
        self.client = ollama
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.1')
        
        # Test Ollama connection
        try:
            self.client.list()
            print(f"✅ Price Tracker: Ollama connected! Using model: {self.model_name}")
        except Exception as e:
            print(f"⚠️  Ollama not running. Start with: ollama serve")
            print(f"   Error: {e}")
    
    async def analyze_price(
        self,
        product_id: int
    ) -> Dict[str, Any]:
        """
        Analyze price for a product and provide recommendation
        
        This function:
        1. Gets price history from database
        2. Calculates trends and statistics
        3. Uses AI to generate recommendation
        4. Returns complete analysis
        
        Args:
            product_id: ID of product to analyze
            
        Returns:
            Complete price analysis with AI recommendation
            
        Example Output:
        {
            "success": True,
            "product_id": 123,
            "product_name": "OnePlus Bullets",
            "price_data": {
                "current_price": 26192,
                "average_price": 27800,
                "min_price": 24500,
                "trend": "decreasing"
            },
            "recommendation": "BUY NOW - Price at all-time low!",
            "confidence": "high"
        }
        """
        db = next(get_db())
        
        try:
            logger.info(f"Analyzing price for product {product_id}")
            
            # Get product details
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return {
                    "success": False,
                    "error": f"Product {product_id} not found"
                }
            
            # Get price trend analysis
            trend_data = await price_tools.calculate_price_trend(
                db=db,
                product_id=product_id
            )
            
            # Get price history
            history = await price_tools.get_price_history(
                db=db,
                product_id=product_id,
                days=30
            )
            
            # Generate AI recommendation using Ollama (async)
            ai_recommendation = await self._generate_ai_recommendation(
                product_name=product.name,
                trend_data=trend_data,
                history_count=len(history)
            )
            
            return {
                "success": True,
                "product_id": product_id,
                "product_name": product.name,
                "price_data": trend_data,
                "history": history[:10],  # Return last 10 days only
                "ai_recommendation": ai_recommendation,
                "recommendation": trend_data.get('recommendation'),
                "confidence": self._calculate_confidence(trend_data)
            }
            
        except Exception as e:
            logger.error(f"Price analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def _generate_ai_recommendation(
        self,
        product_name: str,
        trend_data: Dict[str, Any],
        history_count: int
    ) -> str:
        """
        Use Ollama AI to generate human-friendly recommendation (async)
        
        Args:
            product_name: Name of product
            trend_data: Price trend statistics
            history_count: Number of days of price data
            
        Returns:
            AI-generated recommendation text
        """
        # Build prompt for AI
        prompt = f"""You are a price analysis expert helping shoppers make smart buying decisions.

Analyze this price data for "{product_name}":

📊 PRICE STATISTICS:
- Current Price: ₹{trend_data.get('current_price', 0):,.0f}
- Average Price (30 days): ₹{trend_data.get('average_price', 0):,.0f}
- Lowest Price: ₹{trend_data.get('min_price', 0):,.0f}
- Highest Price: ₹{trend_data.get('max_price', 0):,.0f}

📈 TREND ANALYSIS:
- Trend: {trend_data.get('trend', 'unknown').upper()}
- Price Change: {trend_data.get('price_change_pct', 0):.1f}%
- Data Points: {history_count} days

🎯 SYSTEM RECOMMENDATION: {trend_data.get('recommendation', 'wait').upper()}

Provide a recommendation in 2-3 sentences:
1. Should the user BUY NOW or WAIT?
2. Why? (based on the data)
3. What's the confidence level? (high/medium/low)

Keep it conversational and helpful. Start with your recommendation."""

        try:
            # AGENTIC AI: Async LLM call with timeout
            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_running_loop()
            
            def _generate_sync():
                return self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        'temperature': 0.7,
                        'num_predict': 200
                    }
                )['response'].strip()
            
            # Execute with timeout
            response_text = await asyncio.wait_for(
                loop.run_in_executor(executor, _generate_sync),
                timeout=25.0
            )
            executor.shutdown(wait=False)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Ollama recommendation error: {e}")
            
            # Fallback to rule-based recommendation
            rec = trend_data.get('recommendation', 'wait')
            current = trend_data.get('current_price', 0)
            avg = trend_data.get('average_price', 0)
            
            if rec == 'buy_now':
                return f"✅ BUY NOW! Price is at ₹{current:,.0f}, which is near the all-time low. This is an excellent time to purchase."
            elif rec == 'good_time':
                return f"👍 GOOD DEAL! Current price (₹{current:,.0f}) is below the 30-day average (₹{avg:,.0f}). Fair time to buy."
            else:
                return f"⏳ WAIT! Price is currently ₹{current:,.0f}, which is above average. Consider waiting for a better deal."
    
    def _calculate_confidence(self, trend_data: Dict[str, Any]) -> str:
        """
        Calculate confidence level in recommendation
        
        Args:
            trend_data: Price trend statistics
            
        Returns:
            "high", "medium", or "low"
        """
        data_points = trend_data.get('data_points', 0)
        current = trend_data.get('current_price', 0)
        min_price = trend_data.get('min_price', 1)
        
        # High confidence: lots of data + price near minimum
        if data_points >= 20 and current <= min_price * 1.05:
            return "high"
        
        # Medium confidence: decent data
        elif data_points >= 10:
            return "medium"
        
        # Low confidence: insufficient data
        else:
            return "low"
    
    async def find_best_deals(
        self,
        category: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Find best deals across all products
        
        Args:
            category: Filter by category (optional)
            limit: Maximum number of deals to return
            
        Returns:
            List of best deals with discount info
            
        Example:
            deals = await find_best_deals(category="Electronics", limit=5)
            # Returns top 5 electronics deals
        """
        db = next(get_db())
        
        try:
            deals = await price_tools.find_deals(
                db=db,
                category=category,
                min_discount=10.0,  # At least 10% discount
                limit=limit
            )
            
            return {
                "success": True,
                "deals": deals,
                "count": len(deals),
                "category": category or "All Categories"
            }
            
        except Exception as e:
            logger.error(f"Find deals error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def compare_prices(
        self,
        product_ids: list
    ) -> Dict[str, Any]:
        """
        Compare prices across multiple products
        
        Args:
            product_ids: List of product IDs to compare
            
        Returns:
            Price comparison data for all products
        """
        comparisons = []
        
        for product_id in product_ids:
            analysis = await self.analyze_price(product_id)
            if analysis.get('success'):
                comparisons.append({
                    "product_id": product_id,
                    "product_name": analysis['product_name'],
                    "current_price": analysis['price_data']['current_price'],
                    "trend": analysis['price_data']['trend'],
                    "recommendation": analysis['recommendation']
                })
        
        return {
            "success": True,
            "comparisons": comparisons,
            "count": len(comparisons)
        }


# Global instance for easy importing
price_tracker_agent = PriceTrackerAgent()
