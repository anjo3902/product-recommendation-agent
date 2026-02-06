"""
Comparison Specialist Agent - AI-Powered Product Comparison
Compares products and provides intelligent recommendations

WORKFLOW:
1. User searches for products (e.g., "gaming laptop under 60000")
2. Product Search Agent suggests 3-5 products
3. User asks to compare: "Compare these products"
4. Comparison Agent analyzes and declares winner
5. User makes informed purchase decision

This agent works AFTER product search to help users decide between options.
"""

import ollama
import asyncio
from src.tools.comparison_tools import comparison_tools
from src.database.connection import get_db
from src.utils.cache import comparison_cache
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# Agent Instructions
COMPARISON_AGENT_INSTRUCTIONS = """
You are a Comparison Specialist Agent - an expert at comparing products and helping users make informed decisions.

**Your Mission:**
Help users choose between multiple products by providing clear, objective comparisons.

**Comparison Dimensions:**
1. Price & Value - Which offers better value for money?
2. Performance - Speed, efficiency, capabilities
3. Features - What's included vs missing
4. Build Quality - Materials, durability
5. User Reviews - What real users say
6. Use Case Fit - Best for specific needs

**Comparison Styles You Support:**
1. TABLE - Grid format, easy to scan side-by-side
2. WINNER - Direct recommendation with clear reasoning
3. BATTLE - Engaging round-by-round format
4. DETAILED - Technical specification analysis
5. USE_CASE - "Best for X" recommendations

**Key Principles:**
✓ Be objective - use data, not opinions
✓ Highlight meaningful differences (not minor specs)
✓ Consider user's stated priorities
✓ Recommend based on value, not just price
✓ Acknowledge trade-offs clearly

**Output Format:**
- Start with key differentiators
- Provide winner for each category
- Give final recommendation
- Include use case suggestions

**Example:**
"Samsung S24 wins on camera quality (50MP vs 12MP), but OnePlus 12 wins on battery (5000mAh vs 4000mAh) and price (₹37,000 cheaper). 

For photographers: Samsung S24
For everyday use: OnePlus 12 (better value)"
"""


class ComparisonAgent:
    """AI-powered product comparison agent"""
    
    def __init__(self):
        """Initialize comparison agent with Ollama"""
        try:
            # Test Ollama connection
            ollama.list()
            self.client = ollama
            self.model_name = 'llama3.1'
            logger.info("[OK] Comparison Agent: Ollama connected! Using model: llama3.1")
        except Exception as e:
            logger.error(f"[ERROR] Ollama connection failed: {e}")
            logger.info("[INFO] Make sure Ollama is running: ollama serve")
            self.client = None
            self.model_name = None
    
    async def compare_products(
        self,
        product_ids: List[int],
        comparison_style: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Compare multiple products with caching
        
        Args:
            product_ids: List of product IDs to compare (2-5 products)
            comparison_style: Style of comparison (table, battle, winner, detailed, use_case)
            
        Returns:
            Comparison results with AI analysis
        """
        # Check cache first
        cache_key = f"comparison_{'_'.join(map(str, sorted(product_ids)))}_{comparison_style}"
        cached_result = comparison_cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached comparison for products {product_ids}")
            return cached_result
        
        db = next(get_db())
        
        try:
            # Validate input
            if len(product_ids) < 2:
                return {
                    "success": False,
                    "error": "Need at least 2 products to compare"
                }
            
            if len(product_ids) > 5:
                return {
                    "success": False,
                    "error": "Maximum 5 products can be compared at once"
                }
            
            # Fetch products
            products = await comparison_tools.get_products_for_comparison(db, product_ids)
            
            if len(products) < len(product_ids):
                return {
                    "success": False,
                    "error": f"Only found {len(products)} out of {len(product_ids)} products"
                }
            
            # Calculate differences
            differences = await comparison_tools.calculate_differences(products)
            
            # Determine winners
            winners = await comparison_tools.determine_winners(products)
            
            # Generate comparison based on style
            if comparison_style == "table":
                comparison_output = await comparison_tools.generate_comparison_table(products)
            elif comparison_style == "battle" and len(products) == 2:
                comparison_output = await comparison_tools.generate_battle_comparison(products)
            else:
                comparison_output = None
            
            # Generate AI analysis
            ai_analysis = await self._generate_ai_comparison(
                products, differences, winners, comparison_style
            )
            
            result = {
                "success": True,
                "products": products,
                "differences": differences,
                "winners": winners,
                "comparison_output": comparison_output,
                "ai_analysis": ai_analysis,
                "comparison_style": comparison_style
            }
            
            # Cache the result for 5 minutes
            comparison_cache.set(cache_key, result)
            logger.info(f"Cached comparison for products {product_ids}")
            
            return result
            
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def compare_search_results(
        self,
        search_query: str,
        top_n: int = 3,
        comparison_style: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Search for products and compare top results
        
        This method combines product search + comparison in one workflow:
        1. Search for products matching query
        2. Take top N results
        3. Compare them
        4. Return winner recommendation
        
        Args:
            search_query: User's search query (e.g., "gaming laptop under 60000")
            top_n: Number of top products to compare (2-5)
            comparison_style: Style of comparison
            
        Returns:
            Search results + comparison analysis + winner
            
        Example:
            User: "Compare wireless headphones under 5000"
            Agent: Searches → Finds top 3 → Compares → Declares winner
        """
        from src.agents.product_search_agent import ProductSearchAgent
        
        try:
            # Create search agent instance
            search_agent = ProductSearchAgent()
            
            # Validate top_n
            if top_n < 2:
                top_n = 2
            elif top_n > 5:
                top_n = 5
            
            # Step 1: Search for products
            logger.info(f"[SEARCH] Searching for: {search_query}")
            search_result = search_agent.search_products(
                query=search_query,
                limit=top_n
            )
            
            if not search_result.get('success'):
                return {
                    "success": False,
                    "error": "Product search failed",
                    "details": search_result.get('error')
                }
            
            products_found = search_result.get('products', [])
            
            if len(products_found) < 2:
                return {
                    "success": False,
                    "error": f"Found only {len(products_found)} product(s). Need at least 2 to compare.",
                    "search_query": search_query
                }
            
            # Step 2: Extract product IDs
            product_ids = [p['id'] for p in products_found[:top_n]]
            
            logger.info(f"[DATA] Comparing top {len(product_ids)} products")
            
            # Step 3: Compare products
            comparison_result = await self.compare_products(
                product_ids=product_ids,
                comparison_style=comparison_style
            )
            
            if not comparison_result.get('success'):
                return comparison_result
            
            # Step 4: Add search context
            comparison_result['search_query'] = search_query
            comparison_result['search_results_count'] = len(products_found)
            comparison_result['workflow'] = "search_then_compare"
            
            # Step 5: Generate user-friendly summary
            comparison_result['summary'] = self._generate_workflow_summary(
                search_query, comparison_result
            )
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"Search + Compare workflow error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_workflow_summary(
        self,
        search_query: str,
        comparison_result: Dict[str, Any]
    ) -> str:
        """Generate user-friendly summary of search + compare workflow"""
        
        products = comparison_result.get('products', [])
        winners = comparison_result.get('winners', {})
        
        summary = []
        summary.append(f"[SEARCH] SEARCH: '{search_query}'")
        summary.append(f"[DATA] FOUND: {len(products)} products")
        summary.append("")
        summary.append("🏆 COMPARISON RESULTS:")
        summary.append(f"   • Best Price: {winners.get('best_price', {}).get('product', 'N/A')}")
        summary.append(f"   • Best Rating: {winners.get('best_rating', {}).get('product', 'N/A')}")
        summary.append(f"   • Best Value: {winners.get('best_value', {}).get('product', 'N/A')}")
        summary.append(f"   • OVERALL WINNER: {winners.get('best_overall', {}).get('product', 'N/A')}")
        summary.append("")
        summary.append("[INFO] RECOMMENDATION:")
        summary.append(f"   Based on your search, we recommend: {winners.get('best_overall', {}).get('product', 'N/A')}")
        summary.append(f"   {winners.get('best_overall', {}).get('reason', '')}")
        
        return "\n".join(summary)
    
    async def _generate_ai_comparison(
        self,
        products: List[Dict[str, Any]],
        differences: Dict[str, Any],
        winners: Dict[str, Dict[str, Any]],
        style: str
    ) -> str:
        """
        Generate AI-powered comparison analysis
        
        Args:
            products: List of product dictionaries
            differences: Calculated differences
            winners: Determined winners
            style: Comparison style
            
        Returns:
            AI-generated comparison text
        """
        if not self.client:
            return self._generate_fallback_comparison(products, winners)
        
        try:
            # AGENTIC AI OPTIMIZATION: Concise prompt for faster inference
            product_names = [p['name'] for p in products]
            
            prompt = f"""Compare {len(products)} products:

{self._format_products_for_ai(products)}

Price: ₹{differences['price_analysis']['cheapest']:,.0f}-₹{differences['price_analysis']['most_expensive']:,.0f}
Ratings: {differences['rating_analysis']['lowest_rated']}-{differences['rating_analysis']['highest_rated']}/5
Best Deal: {differences['discount_analysis']['best_discount']}% off {differences['discount_analysis']['best_deal_product']}

Winners:
• Price: {winners['best_price']['product']}
• Rating: {winners['best_rating']['product']}
• Value: {winners['best_value']['product']}
• Overall: {winners['best_overall']['product']}

Provide:
1. Key differences
2. Category winners
3. Recommendation
4. Best for scenarios

{style.upper()} style. 200 words max."""
            
            # AGENTIC AI: Async comparison with proper timeout
            try:
                if self.client:
                    import concurrent.futures
                    import traceback
                    
                    def _generate_sync():
                        try:
                            response = ollama.generate(
                                model=self.model_name,
                                prompt=prompt,
                                options={
                                    'num_predict': 120,  # Reduced from 150 for faster response
                                    'temperature': 0.3,  # Consistent output
                                    'top_p': 0.9  # Nucleus sampling for quality
                                }
                            )
                            return response['response']
                        except Exception as inner_e:
                            logger.error(f"Ollama generate error: {inner_e}")
                            traceback.print_exc()
                            raise
                    
                    loop = asyncio.get_running_loop()
                    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                    
                    # AGENTIC AI OPTIMIZATION: Reduced timeout for faster UX
                    ai_response = await asyncio.wait_for(
                        loop.run_in_executor(executor, _generate_sync),
                        timeout=50.0  # Reduced from 90s: 44% faster!
                    )
                    executor.shutdown(wait=False)
                    logger.info(f"[OK] LLM comparison completed for {len(products)} products")
                    return ai_response
                else:
                    raise Exception("Ollama client not available")
            except asyncio.TimeoutError as e:
                logger.warning(f"AI comparison timeout after 50s, using rule-based fallback")
                return self._generate_fallback_comparison(products, winners)
            
        except Exception as e:
            logger.error(f"AI comparison generation error: {e}")
            return self._generate_fallback_comparison(products, winners)
    
    def _format_products_for_ai(self, products: List[Dict[str, Any]]) -> str:
        """Format product data for AI prompt"""
        formatted = []
        
        for i, product in enumerate(products, 1):
            mrp_value = product['mrp'] if product['mrp'] else product['price']
            formatted.append(f"""
Product {i}: {product['name']}
- Brand: {product['brand']}
- Price: ₹{product['price']:,.0f} (MRP: ₹{mrp_value:,.0f})
- Discount: {product['discount_pct']}% OFF
- Rating: {product['rating']}/5 ({product['review_count']} reviews)
- In Stock: {'Yes' if product['in_stock'] else 'No'}
""")
        
        return "\n".join(formatted)
    
    def _generate_fallback_comparison(
        self,
        products: List[Dict[str, Any]],
        winners: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate rule-based comparison when AI is unavailable"""
        
        comparison = []
        comparison.append("[DATA] COMPARISON ANALYSIS")
        comparison.append("")
        
        # Price comparison
        prices = sorted(products, key=lambda p: p['price'])
        comparison.append(f"💰 PRICE WINNER: {prices[0]['name']}")
        comparison.append(f"   ₹{prices[0]['price']:,.0f} (cheapest)")
        if len(prices) > 1:
            comparison.append(f"   Save ₹{(prices[-1]['price'] - prices[0]['price']):,.0f} vs most expensive")
        comparison.append("")
        
        # Rating comparison
        ratings = sorted(products, key=lambda p: p['rating'], reverse=True)
        comparison.append(f"⭐ RATING WINNER: {ratings[0]['name']}")
        comparison.append(f"   {ratings[0]['rating']}/5 ({ratings[0]['review_count']} reviews)")
        comparison.append("")
        
        # Value comparison
        comparison.append(f"[TARGET] BEST OVERALL: {winners['best_overall']['product']}")
        comparison.append(f"   {winners['best_overall']['reason']}")
        comparison.append("")
        
        # Recommendations
        comparison.append("[INFO] RECOMMENDATIONS:")
        comparison.append(f"   • For budget: {prices[0]['name']}")
        comparison.append(f"   • For quality: {ratings[0]['name']}")
        comparison.append(f"   • For value: {winners['best_overall']['product']}")
        
        return "\n".join(comparison)
    
    async def get_winner_recommendation(
        self,
        product_ids: List[int],
        use_case: str = None
    ) -> Dict[str, Any]:
        """
        Get direct winner recommendation
        
        Args:
            product_ids: List of product IDs
            use_case: Specific use case (e.g., "gaming", "photography", "budget")
            
        Returns:
            Winner recommendation with reasoning
        """
        db = next(get_db())
        
        try:
            # Fetch products
            products = await comparison_tools.get_products_for_comparison(db, product_ids)
            
            if not products:
                return {
                    "success": False,
                    "error": "No products found"
                }
            
            # Determine winners
            winners = await comparison_tools.determine_winners(products)
            
            # Select winner based on use case
            if use_case:
                winner = await self._select_use_case_winner(products, use_case)
            else:
                # Default: best overall
                winner_name = winners['best_overall']['product']
                winner = next(p for p in products if p['name'] == winner_name)
            
            return {
                "success": True,
                "winner": winner,
                "reason": self._explain_winner_choice(winner, products, use_case),
                "alternatives": [p for p in products if p['id'] != winner['id']][:2]
            }
            
        except Exception as e:
            logger.error(f"Winner recommendation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def _select_use_case_winner(
        self,
        products: List[Dict[str, Any]],
        use_case: str
    ) -> Dict[str, Any]:
        """Select winner based on specific use case"""
        
        use_case_lower = use_case.lower()
        
        # Budget use case
        if 'budget' in use_case_lower or 'cheap' in use_case_lower:
            return min(products, key=lambda p: p['price'])
        
        # Quality use case
        elif 'quality' in use_case_lower or 'best' in use_case_lower:
            return max(products, key=lambda p: p['rating'])
        
        # Gaming use case (look for gaming keywords in features)
        elif 'gaming' in use_case_lower or 'game' in use_case_lower:
            gaming_products = [p for p in products if any('gaming' in f.lower() for f in p.get('features', []))]
            if gaming_products:
                return max(gaming_products, key=lambda p: p['rating'])
        
        # Default: best value
        for product in products:
            product['value_score'] = (product['rating'] * product['review_count']) / (product['price'] / 1000)
        
        return max(products, key=lambda p: p['value_score'])
    
    def _explain_winner_choice(
        self,
        winner: Dict[str, Any],
        all_products: List[Dict[str, Any]],
        use_case: str = None
    ) -> str:
        """Explain why this product won"""
        
        reasons = []
        
        if use_case:
            reasons.append(f"Best match for: {use_case}")
        
        # Price advantage
        if winner['price'] == min(p['price'] for p in all_products):
            reasons.append(f"Lowest price: ₹{winner['price']:,.0f}")
        
        # Rating advantage
        if winner['rating'] == max(p['rating'] for p in all_products):
            reasons.append(f"Highest rated: {winner['rating']}/5")
        
        # Discount advantage
        if winner['discount_pct'] == max(p['discount_pct'] for p in all_products):
            reasons.append(f"Best discount: {winner['discount_pct']}% OFF")
        
        if not reasons:
            reasons.append("Best overall value")
        
        return " | ".join(reasons)


# Global instance
comparison_agent = ComparisonAgent()
