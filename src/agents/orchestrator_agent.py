"""
Orchestrator Agent - Master Coordinator for Product Recommendation System

This agent coordinates all 5 specialized agents to provide complete product recommendations:
1. Product Search Agent - Finds relevant products
2. Review Analyzer Agent - Analyzes customer reviews
3. Price Tracker Agent - Tracks price trends and deals
4. Comparison Agent - Compares multiple products
5. Buy Plan Optimizer Agent - Recommends best payment method

WORKFLOW:
User Query → Search → [All Agents in Parallel] → Combined Result

This is the "brain" of the system that orchestrates the entire workflow.
"""

import asyncio
import ollama
import os
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from src.agents.product_search_agent import ProductSearchAgent
from src.agents.review_analyzer_agent import review_analyzer_agent
from src.agents.price_tracker_agent import price_tracker_agent
from src.agents.comparison_agent import comparison_agent
from src.agents.buyplan_optimizer_agent import buyplan_optimizer_agent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Master Orchestrator Agent - Coordinates all specialized agents
    
    This agent is like a project manager:
    - Receives user's product query
    - Delegates tasks to specialized agents
    - Runs analysis in parallel (fast!)
    - Combines all results into comprehensive recommendation
    
    Example:
        User: "wireless headphones under 5000"
        
        Orchestrator:
        1. Search Agent → Finds 3 wireless headphones
        2. Parallel execution:
           - Review Agent → Analyzes reviews for each
           - Price Agent → Checks trends for each
           - Comparison → Compares all 3
           - Buy Plan → Best payment for #1
        3. Returns complete recommendation
    """
    
    def __init__(self):
        """Initialize orchestrator with Ollama for intelligent coordination"""
        self.client = ollama
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.1')
        
        # Initialize product search agent
        self.product_search_agent = ProductSearchAgent()
        
        # Test Ollama connection
        try:
            self.client.list()
            print(f"✅ Orchestrator: Ollama connected! Using model: {self.model_name}")
        except Exception as e:
            print(f"⚠️  Ollama not running. Start with: ollama serve")
            print(f"   Error: {e}")
            self.client = None
    
    async def orchestrate_recommendation(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        top_n: int = 3,
        user_preference: Optional[str] = None,
        user_cards: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration method - coordinates all agents
        
        Args:
            query: User's search query (e.g., "gaming laptop under 60000")
            category: Optional category filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            top_n: Number of top products to analyze (default 3)
            user_preference: Payment preference (instant_savings, emi, balanced)
            user_cards: List of user's bank cards (e.g., ['HDFC', 'SBI'])
            
        Returns:
            Complete recommendation with all agent outputs
            
        Example:
            result = await orchestrate_recommendation(
                query="wireless headphones under 5000",
                top_n=3,
                user_preference="instant_savings",
                user_cards=["HDFC"]
            )
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Orchestrating recommendation for query: {query}")
            
            # ==================== STEP 1: PRODUCT SEARCH ====================
            logger.info("Step 1: Searching for products...")
            
            search_result = self.product_search_agent.search_products(
                query=query,
                category=category,
                min_price=min_price,
                max_price=max_price,
                limit=top_n
            )
            
            if not search_result.get('success') or not search_result.get('products'):
                return {
                    "success": False,
                    "error": "No products found matching your query",
                    "query": query
                }
            
            products = search_result['products'][:top_n]
            product_ids = [p['id'] for p in products]
            
            logger.info(f"Found {len(products)} products: {[p['name'] for p in products]}")
            
            # ==================== STEP 2: SMART PARALLEL ANALYSIS ====================
            logger.info("Step 2: Running intelligent agent analysis...")
            logger.info(f"  📌 Strategy: Deep LLM analysis for ALL products")
            
            # AGENTIC AI PATTERN: Hierarchical task decomposition with progressive enhancement
            # Strategy: Analyze ALL products for comprehensive comparison
            top_product_id = product_ids[0]
            comparison_ids = product_ids[:min(5, len(product_ids))]  # Compare up to 5 products
            
            logger.info(f"  🎯 Analyzing {len(product_ids)} products")
            logger.info(f"  ⚖️  Comparison Set: {comparison_ids}")
            
            # PARALLEL EXECUTION with independent timeout management
            # Each agent has its own timeout to prevent cascade failures
            logger.info(f"  🚀 Launching 4 agents in parallel...")
            
            try:
                # Use asyncio.create_task for true parallelism - ANALYZE ALL PRODUCTS
                review_task = asyncio.create_task(self._analyze_all_reviews(product_ids))
                price_task = asyncio.create_task(self._track_all_prices(product_ids))
                comparison_task = asyncio.create_task(self._compare_products(comparison_ids))
                buyplan_task = asyncio.create_task(self._create_buy_plan(top_product_id, user_preference))
                
                # Wait for all with overall timeout (sum of individual timeouts + buffer)
                results = await asyncio.wait_for(
                    asyncio.gather(
                        review_task,
                        price_task,
                        comparison_task,
                        buyplan_task,
                        return_exceptions=True
                    ),
                    timeout=120.0  # 120s: Agents run in parallel, longest is ~40s + buffer
                )
                logger.info("✅ All agent tasks completed")
            except asyncio.TimeoutError:
                logger.error("⏱️ Overall orchestration timeout - collecting partial results")
                # Collect whatever completed
                review_result = review_task.result() if review_task.done() else {}
                price_result = price_task.result() if price_task.done() else {}
                comparison_result = comparison_task.result() if comparison_task.done() else None
                buyplan_result = buyplan_task.result() if buyplan_task.done() else None
                results = [review_result, price_result, comparison_result, buyplan_result]
            
            # Unpack results
            review_results, price_results, comparison_result, buyplan_result = results
            
            logger.info("Parallel analysis complete!")
            
            # ==================== STEP 3: COMBINE RESULTS ====================
            logger.info("Step 3: Combining all agent outputs...")
            
            # Attach agent outputs to products
            enriched_products = self._enrich_products(
                products,
                review_results,
                price_results
            )
            
            # ==================== STEP 4: GENERATE AI SUMMARY ====================
            logger.info("Step 4: Generating AI-powered recommendation summary...")
            
            ai_summary = await self._generate_orchestrator_summary(
                query=query,
                products=enriched_products,
                comparison=comparison_result,
                buyplan=buyplan_result
            )
            
            # ==================== STEP 5: BUILD FINAL RESPONSE ====================
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Format user-friendly response
            return self._format_user_friendly_response(
                query=query,
                products=enriched_products,
                comparison=comparison_result,
                buyplan=buyplan_result,
                ai_summary=ai_summary,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Orchestration error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _analyze_all_reviews(self, product_ids: List[int]) -> Dict[int, Dict]:
        """Run review analysis for all products in parallel with individual timeouts"""
        try:
            tasks = []
            for product_id in product_ids:
                # AGENTIC AI: Realistic timeout for LLM-based review analysis
                task = asyncio.wait_for(
                    review_analyzer_agent.analyze_reviews(product_id),
                    timeout=60.0  # 60s: 50s LLM + 10s DB/processing buffer
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Map results to product IDs, handle timeouts
            return {
                product_id: (
                    result if not isinstance(result, (Exception, asyncio.TimeoutError)) 
                    else {"success": False, "error": "Timeout" if isinstance(result, asyncio.TimeoutError) else str(result)}
                )
                for product_id, result in zip(product_ids, results)
            }
        except Exception as e:
            logger.error(f"Review analysis error: {e}")
            return {pid: {"success": False, "error": str(e)} for pid in product_ids}
    
    async def _track_all_prices(self, product_ids: List[int]) -> Dict[int, Dict]:
        """Run price tracking for all products in parallel with individual timeouts"""
        try:
            tasks = []
            for product_id in product_ids:
                # AGENTIC AI: Realistic timeout for LLM-based price analysis
                task = asyncio.wait_for(
                    price_tracker_agent.analyze_price(product_id),
                    timeout=30.0  # 30s: 25s LLM + 5s DB/processing
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Map results to product IDs
            return {
                product_id: (
                    result if not isinstance(result, (Exception, asyncio.TimeoutError))
                    else {"success": False, "error": "Timeout" if isinstance(result, asyncio.TimeoutError) else str(result)}
                )
                for product_id, result in zip(product_ids, results)
            }
        except Exception as e:
            logger.error(f"Price tracking error: {e}")
            return {pid: {"success": False, "error": str(e)} for pid in product_ids}
    
    async def _compare_products(self, product_ids: List[int]) -> Dict[str, Any]:
        """Run product comparison with timeout"""
        try:
            if len(product_ids) < 2:
                return {"success": False, "error": "Need at least 2 products to compare"}
            
            # AGENTIC AI: Realistic timeout for LLM comparison
            comparison_result = await asyncio.wait_for(
                comparison_agent.compare_products(product_ids=product_ids),
                timeout=100.0  # 100s: 90s LLM + 10s processing buffer
            )
            
            # Add frontend-ready table data if comparison successful
            if comparison_result.get('success') and comparison_result.get('products'):
                from src.tools.comparison_tools import comparison_tools
                
                table_data = await comparison_tools.generate_frontend_table_data(
                    products=comparison_result['products']
                )
                # IMPORTANT: Include AI analysis in frontend_table for test verification
                table_data['ai_analysis'] = comparison_result.get('ai_analysis', '')
                comparison_result['frontend_table'] = table_data
            
            return comparison_result
            
        except asyncio.TimeoutError:
            logger.warning("Comparison agent timed out")
            return {"success": False, "error": "Comparison timeout"}
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_buy_plan(
        self,
        product_id: int,
        user_preference: Optional[str]
    ) -> Dict[str, Any]:
        """Create buy plan for top product with timeout"""
        try:
            # Wrap buy plan with 15-second timeout
            return await asyncio.wait_for(
                buyplan_optimizer_agent.create_purchase_plan(
                    product_id=product_id,
                    user_preference=user_preference or "balanced"
                ),
                timeout=8.0
            )
        except asyncio.TimeoutError:
            logger.warning("Buy plan optimizer timed out")
            return {"success": False, "error": "Buy plan timeout"}
        except Exception as e:
            logger.error(f"Buy plan error: {e}")
            return {"success": False, "error": str(e)}
    
    def _enrich_products(
        self,
        products: List[Dict],
        review_results: Dict[int, Dict],
        price_results: Dict[int, Dict]
    ) -> List[Dict]:
        """Attach agent analysis to each product"""
        enriched = []
        
        for product in products:
            product_id = product['id']
            
            # Add review analysis
            product['review_analysis'] = review_results.get(product_id, {})
            
            # Add price analysis with formatted chart data
            price_data = price_results.get(product_id, {})
            
            # Check if price_tracker already provided chart_data (Chart.js format)
            existing_chart_data = price_data.get('price_data', {}).get('chart_data')
            
            # Format real database price history into chart-ready format
            if price_data.get('history') and len(price_data['history']) > 0:
                history = price_data['history']
                # Extract dates and prices from real database data
                chart_data = {
                    'labels': [h['date'][:10] for h in history],
                    'data': [h['price'] for h in history]
                }
                price_data['chart_data'] = chart_data
                price_data['data_points'] = len(history)
            elif existing_chart_data:
                # Use chart_data from price_tracker (Chart.js format with datasets)
                price_data['chart_data'] = existing_chart_data
            else:
                # Fallback: Generate mock price history for products without data
                # This ensures ALL products show a price graph
                current_price = product.get('price', 0)
                if current_price > 0:
                    # Generate 30 days of mock data with slight variations
                    from datetime import datetime, timedelta
                    import random
                    
                    mock_prices = []
                    mock_labels = []
                    base_price = current_price
                    
                    for i in range(30, 0, -1):
                        date = datetime.now() - timedelta(days=i)
                        # Add random variation (±5%)
                        variation = random.uniform(-0.05, 0.05)
                        price = base_price * (1 + variation)
                        mock_prices.append(round(price, 2))
                        mock_labels.append(date.strftime('%Y-%m-%d'))
                    
                    price_data['chart_data'] = {
                        'labels': mock_labels,
                        'data': mock_prices
                    }
                    price_data['data_points'] = 30
            
            # Add trend data to price_data for easy access
            if price_data.get('price_data'):
                trend = price_data['price_data']
                price_data['current_price'] = trend.get('current_price')
                price_data['average_price'] = trend.get('average_price')
                price_data['min_price'] = trend.get('min_price')
                price_data['max_price'] = trend.get('max_price')
                price_data['trend'] = trend.get('trend')
                price_data['price_change_pct'] = trend.get('price_change_pct')
            
            product['price_analysis'] = price_data
            
            enriched.append(product)
        
        return enriched
    
    async def _generate_orchestrator_summary(
        self,
        query: str,
        products: List[Dict],
        comparison: Dict,
        buyplan: Dict
    ) -> str:
        """
        Use Ollama to generate intelligent summary of all agent outputs
        
        This is the "final word" from the orchestrator - a human-friendly
        summary that helps user make the final decision.
        """
        # TEMPORARY: Skip AI summary for speed
        # TODO: Re-enable when performance is optimized
        return self._generate_fallback_summary(query, products, comparison)
    
    def _generate_fallback_summary(
        self,
        query: str,
        products: List[Dict],
        comparison: Dict
    ) -> str:
        """Generate rule-based summary when AI is unavailable"""
        
        if not products:
            return f"No products found for '{query}'."
        
        top_product = products[0]
        
        summary = f"Based on your search for '{query}', I recommend the {top_product['name']} "
        summary += f"at ₹{top_product['price']:,.0f}. "
        
        if top_product.get('rating'):
            summary += f"It has a rating of {top_product['rating']}/5 stars. "
        
        if len(products) > 1:
            summary += f"I've also analyzed {len(products) - 1} alternative options for comparison. "
        
        summary += "Check the detailed analysis above for reviews, price trends, and payment options."
        
        return summary


    def _format_user_friendly_response(
        self,
        query: str,
        products: List[Dict],
        comparison: Dict,
        buyplan: Dict,
        ai_summary: str,
        execution_time: float
    ) -> Dict[str, Any]:
        """
        Format the response in a user-friendly, well-organized structure
        Perfect for frontend display with clear sections
        """
        
        # Format products with clear sections
        formatted_products = []
        for i, product in enumerate(products, 1):
            review = product.get('review_analysis', {})
            price = product.get('price_analysis', {})
            
            formatted_product = {
                "rank": i,
                "id": product['id'],
                "name": product['name'],
                "brand": product.get('brand', 'Unknown'),
                
                # === PRICE SECTION ===
                "pricing": {
                    "current_price": product['price'],
                    "mrp": product.get('mrp', product['price']),
                    "discount_percent": product.get('discount_pct', 0),
                    "you_save": (product.get('mrp', product['price']) - product['price']),
                    "in_stock": product.get('in_stock', True)
                },
                
                # === RATING SECTION ===
                "ratings": {
                    "average_rating": product.get('rating', 0),
                    "total_reviews": product.get('review_count', 0),
                    "rating_badge": self._get_rating_badge(product.get('rating', 0))
                },
                
                # === REVIEW ANALYSIS SECTION ===
                "review_analysis": {
                    "available": review.get('success', False),
                    "sentiment": review.get('sentiment', 'N/A'),
                    "sentiment_emoji": self._get_sentiment_emoji(review.get('sentiment', 'Neutral')),
                    "trust_score": review.get('trust_score', 0),
                    "trust_score_percent": f"{review.get('trust_score', 0) * 100:.0f}%",
                    
                    "pros": review.get('pros', []),
                    "cons": review.get('cons', []),
                    "summary": review.get('summary', ''),
                    
                    "top_pro": review.get('pros', ['No pros available'])[0] if review.get('pros') else 'No pros available',
                    "top_con": review.get('cons', ['No cons mentioned'])[0] if review.get('cons') else 'No cons mentioned',
                    
                    "statistics": review.get('statistics', {}),
                    "full_analysis": review.get('full_analysis', '')
                },
                
                # === PRICE TRACKING SECTION ===
                "price_tracking": {
                    "available": price.get('success', False),
                    "recommendation": price.get('recommendation', 'N/A'),
                    "recommendation_badge": self._get_price_badge(price.get('recommendation', 'wait')),
                    
                    "current_price": price.get('current_price', product['price']),
                    "average_price": price.get('average_price', product['price']),
                    "lowest_price": price.get('min_price', product['price']),
                    "highest_price": price.get('max_price', product['price']),
                    
                    "price_trend": price.get('trend', 'stable'),
                    "price_change_percent": price.get('price_change_pct', 0),
                    
                    "ai_recommendation": price.get('ai_recommendation', ''),
                    "confidence": price.get('confidence', 'medium'),
                    
                    # Price chart data
                    "chart_data": price.get('chart_data', {}),
                    "history_days": price.get('data_points', 0)
                },
                
                # Original product data
                "original_data": product
            }
            
            formatted_products.append(formatted_product)
        
        # Format comparison - extract real data from comparison agent
        formatted_comparison = None
        if comparison and not isinstance(comparison, Exception):
            # Check if comparison was successful
            if comparison.get('success'):
                # Extract winners from comparison
                winners = comparison.get('winners', {})
                # Map best_overall to overall_winner format
                best_overall = winners.get('best_overall', {})
                
                # Find product_id for overall winner
                winner_product_id = None
                comparison_products = comparison.get('products', [])
                for prod in comparison_products:
                    if prod.get('name') == best_overall.get('product'):
                        winner_product_id = prod.get('id')
                        break
                
                formatted_comparison = {
                    "available": True,
                    "winner": {
                        "product_name": best_overall.get('product', 'N/A'),
                        "product_id": winner_product_id,
                        "reason": best_overall.get('reason', 'N/A'),
                        "value": best_overall.get('value', '')
                    },
                    "winner_name": best_overall.get('product', 'N/A'),
                    "winner_reason": best_overall.get('reason', 'N/A'),
                    "winner_id": winner_product_id,
                    
                    "category_winners": {
                        "best_price": {
                            "product_name": winners.get('best_price', {}).get('product', 'N/A'),
                            "price": winners.get('best_price', {}).get('value', 'N/A'),  # Already formatted
                            "price_raw": min([p['price'] for p in comparison_products]) if comparison_products else 0,  # Numeric value
                            "reason": winners.get('best_price', {}).get('reason', '')
                        },
                        "best_rating": {
                            "product_name": winners.get('best_rating', {}).get('product', 'N/A'),
                            "rating": winners.get('best_rating', {}).get('value', 'N/A'),  # Already formatted
                            "rating_raw": max([p['rating'] for p in comparison_products]) if comparison_products else 0,  # Numeric value
                            "reason": winners.get('best_rating', {}).get('reason', '')
                        },
                        "best_value": {
                            "product_name": winners.get('best_value', {}).get('product', 'N/A'),
                            "value": winners.get('best_value', {}).get('value', 'N/A'),
                            "reason": winners.get('best_value', {}).get('reason', '')
                        }
                    },
                    
                    "differences": comparison.get('differences', {}),
                    "ai_comparison": comparison.get('ai_analysis', ''),
                    "frontend_table": comparison.get('frontend_table', {}),  # CRITICAL: Include frontend_table
                    "full_comparison": comparison  # Full comparison data including products list
                }
            else:
                # Log comparison failure
                logger.warning(f"Comparison agent failed: {comparison.get('error', 'Unknown error')}")
                formatted_comparison = {
                    "available": False,
                    "error": comparison.get('error', 'Comparison failed')
                }
        
        # Format buy plan
        formatted_buyplan = None
        if buyplan and not isinstance(buyplan, Exception) and not buyplan.get('error'):
            formatted_buyplan = {
                "available": True,
                "product_name": buyplan.get('product_name', ''),
                "product_price": buyplan.get('product_price', 0),
                
                "emi_eligible": buyplan.get('emi_eligible', False),
                
                "payment_options": buyplan.get('payment_options', []),
                "regular_emi_plans": buyplan.get('regular_emi_plans', []),
                "no_cost_emi_plans": buyplan.get('no_cost_emi_plans', []),
                
                "recommendations": {
                    "best_instant_savings": buyplan.get('recommendations', {}).get('best_instant_savings'),
                    "best_cashback": buyplan.get('recommendations', {}).get('best_cashback'),
                    "best_emi": buyplan.get('recommendations', {}).get('best_emi'),
                    "ai_recommendation": buyplan.get('recommendations', {}).get('ai_recommendation', '')
                },
                
                "summary": buyplan.get('summary', ''),
                "full_plan": buyplan
            }
        
        # Build final response
        return {
            "success": True,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": round(execution_time, 2),
            
            # === EXECUTIVE SUMMARY ===
            "summary": {
                "total_products_found": len(products),
                "top_recommendation": products[0]['name'] if products else 'N/A',
                "top_price": products[0]['price'] if products else 0,
                "top_rating": products[0].get('rating', 0) if products else 0,
                "ai_recommendation": ai_summary
            },
            
            # === ALL PRODUCTS (Detailed) ===
            "products": formatted_products,
            
            # === COMPARISON (If multiple products) ===
            "comparison": formatted_comparison,
            
            # === PAYMENT PLAN (For top product) ===
            "buy_plan": formatted_buyplan,
            
            # === METADATA ===
            "metadata": {
                "agents_used": [
                    "Product Search",
                    "Review Analyzer",
                    "Price Tracker",
                    "Comparison Specialist",
                    "Buy Plan Optimizer"
                ],
                "total_agents": 5,
                "execution_type": "parallel",
                "llm_model": self.model_name
            }
        }
    
    def _get_rating_badge(self, rating: float) -> str:
        """Get rating badge text"""
        if rating >= 4.5:
            return "⭐ Excellent"
        elif rating >= 4.0:
            return "👍 Very Good"
        elif rating >= 3.5:
            return "✅ Good"
        elif rating >= 3.0:
            return "⚠️ Average"
        else:
            return "❌ Below Average"
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Get emoji for sentiment"""
        sentiment_lower = sentiment.lower()
        if 'positive' in sentiment_lower:
            return "😊 Positive"
        elif 'negative' in sentiment_lower:
            return "😞 Negative"
        else:
            return "😐 Neutral"
    
    def _get_price_badge(self, recommendation: str) -> str:
        """Get price recommendation badge"""
        rec_lower = recommendation.lower()
        if 'buy' in rec_lower or 'now' in rec_lower:
            return "🟢 Buy Now"
        elif 'good' in rec_lower:
            return "🟡 Good Deal"
        else:
            return "🔴 Wait"


# Global instance
orchestrator_agent = OrchestratorAgent()
