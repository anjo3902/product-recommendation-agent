# src/agents/review_analyzer_agent.py
import ollama
import os
import asyncio
from src.tools.review_tools import review_tools
from src.database.connection import get_db
from src.utils.cache import review_cache
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ReviewAnalyzerAgent:
    """Review Analyzer Agent using Ollama for sentiment analysis"""
    
    def __init__(self):
        # Ollama configuration
        self.client = ollama
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.1')
        
        # Test Ollama connection
        try:
            self.client.list()
            print(f"✅ Review Analyzer: Ollama connected! Using model: {self.model_name}")
        except Exception as e:
            print(f"⚠️  Ollama not running. Start with: ollama serve")
            print(f"   Error: {e}")
    
    async def analyze_reviews(
        self,
        product_id: int
    ) -> Dict:
        """
        Analyze reviews for a product with caching
        
        Args:
            product_id: Product ID
            
        Returns:
            Review analysis results with pros, cons, sentiment, and summary
        """
        # Check cache first
        cache_key = f"review_analysis_{product_id}"
        cached_result = review_cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached review analysis for product {product_id}")
            return cached_result
        
        db = next(get_db())
        
        try:
            logger.info(f"Analyzing reviews for product {product_id}")
            
            # Get reviews and statistics
            reviews = await review_tools.get_reviews(
                db=db,
                product_id=product_id,
                limit=100
            )
            
            stats = await review_tools.get_review_statistics(
                db=db,
                product_id=product_id
            )
            
            # Extract themes early (needed for both LLM and fallback)
            themes = await review_tools.extract_themes(reviews)
            
            if not reviews:
                return {
                    "success": False,
                    "message": "No reviews found for this product",
                    "product_id": product_id
                }
            
            # AGENTIC AI OPTIMIZATION: Concise prompt for faster LLM inference
            # Strategy: Minimal tokens, focused output, structured format
            avg_rating = stats['average_rating']
            total_reviews = stats['total_reviews']
            verified_pct = (stats['verified_purchases']/total_reviews*100) if total_reviews > 0 else 0
            
            # Extract top themes only (reduce data sent to LLM)
            top_positive = themes['positive'][:3] if themes['positive'] else []
            top_negative = themes['negative'][:2] if themes['negative'] else []
            
            analysis_prompt = f"""Product Review Analysis:
Rating: {avg_rating:.1f}/5 ({total_reviews} reviews, {verified_pct:.0f}% verified)

Positive: {', '.join(top_positive)}
Negative: {', '.join(top_negative)}

Provide:
1. Sentiment (Positive/Neutral/Negative)
2. Top 3 pros (brief)
3. Top 2 cons (brief)
4. One sentence summary

Be concise."""
            
            # Use Ollama AI for intelligent analysis with proper async execution
            try:
                if self.client:
                    # AGENTIC AI PATTERN: Non-blocking LLM call with timeout
                    import concurrent.futures
                    import traceback
                    
                    def _generate_sync():
                        try:
                            response = ollama.generate(
                                model=self.model_name,
                                prompt=analysis_prompt,
                                options={
                                    'num_predict': 150,  # Reduced from 300 for faster inference
                                    'temperature': 0.3    # Lower temperature for consistent output
                                }
                            )
                            return response['response']
                        except Exception as inner_e:
                            logger.error(f"Ollama generate error: {inner_e}")
                            traceback.print_exc()
                            raise
                    
                    loop = asyncio.get_running_loop()
                    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                    
                    # Execute with strict timeout enforcement
                    analysis_text = await asyncio.wait_for(
                        loop.run_in_executor(executor, _generate_sync),
                        timeout=90.0  # 90s timeout: Increased for Ollama local LLM (was 50s)
                    )
                    executor.shutdown(wait=False)
                    logger.info(f"✅ LLM review analysis completed for product {product_id}")
                else:
                    raise Exception("Ollama client not available")
            except asyncio.TimeoutError as e:
                logger.warning(f"AI generation timeout after 50s, using rule-based fallback")
                # Fallback to rule-based analysis (themes already extracted)
                trust_score = self._calculate_trust_score(stats, reviews)
                avg_rating = stats['average_rating']
                sentiment = 'Positive' if avg_rating >= 4 else 'Neutral' if avg_rating >= 3 else 'Negative'
                pros = themes['positive'][:3] if themes['positive'] else ['Overall positive feedback']
                cons = themes['negative'][:2] if themes['negative'] else ['Some concerns noted']
                summary = f"Product rated {avg_rating}/5 by {stats['total_reviews']} customers"
                analysis_text = f"{sentiment} sentiment based on {stats['total_reviews']} reviews"
                
                result = {
                    "success": True,
                    "product_id": product_id,
                    "statistics": stats,
                    "sentiment": sentiment,
                    "pros": pros,
                    "cons": cons,
                    "summary": summary,
                    "trust_score": trust_score,
                    "themes": themes,
                    "full_analysis": analysis_text
                }
                
                # Cache the fallback result
                review_cache.set(cache_key, result)
                logger.info(f"Cached fallback review analysis for product {product_id}")
                return result
            
            # Parse the AI response for structured data
            sentiment, pros, cons, summary = self._parse_ai_response(analysis_text)
            
            # Calculate trust score after successful LLM response
            trust_score = self._calculate_trust_score(stats, reviews)
            
            result = {
                "success": True,
                "product_id": product_id,
                "statistics": stats,
                "sentiment": sentiment,
                "pros": pros,
                "cons": cons,
                "summary": summary,
                "trust_score": trust_score,
                "themes": themes,
                "full_analysis": analysis_text
            }
            
            # Cache the result for 10 minutes
            review_cache.set(cache_key, result)
            logger.info(f"Cached review analysis for product {product_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Review analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "product_id": product_id
            }
        finally:
            db.close()
    
    def _calculate_trust_score(self, stats: Dict, reviews: List[Dict]) -> float:
        """
        Calculate trust score based on review patterns
        
        Args:
            stats: Review statistics
            reviews: List of reviews
            
        Returns:
            Trust score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Factor 1: Verified purchases (max +0.3)
        verified_ratio = stats['verified_purchases'] / stats['total_reviews']
        score += verified_ratio * 0.3
        
        # Factor 2: Balanced distribution (max +0.2)
        # All 5-star or all 1-star = suspicious
        distribution = stats['rating_distribution']
        five_star_ratio = distribution.get(5, 0) / stats['total_reviews']
        one_star_ratio = distribution.get(1, 0) / stats['total_reviews']
        
        if five_star_ratio < 0.7 and one_star_ratio < 0.3:
            score += 0.2  # Good balance
        elif five_star_ratio > 0.9:
            score -= 0.1  # Suspiciously high
        
        # Factor 3: Sample size (max +0.1)
        if stats['total_reviews'] > 50:
            score += 0.1
        elif stats['total_reviews'] > 20:
            score += 0.05
        
        return min(max(score, 0), 1)  # Clamp between 0 and 1
    
    def _parse_ai_response(self, text: str) -> tuple:
        """
        Parse AI response into structured components
        
        Args:
            text: AI-generated analysis text
            
        Returns:
            Tuple of (sentiment, pros, cons, summary)
        """
        sentiment = "Neutral"
        pros = []
        cons = []
        summary = ""
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect sentiment
            if 'SENTIMENT' in line.upper() or 'OVERALL' in line.upper():
                if 'positive' in line.lower():
                    sentiment = "Positive"
                elif 'negative' in line.lower():
                    sentiment = "Negative"
                elif 'neutral' in line.lower():
                    sentiment = "Neutral"
            
            # Detect sections
            elif 'PROS' in line.upper() or 'ADVANTAGES' in line.upper():
                current_section = 'pros'
            elif 'CONS' in line.upper() or 'DISADVANTAGES' in line.upper():
                current_section = 'cons'
            elif 'SUMMARY' in line.upper():
                current_section = 'summary'
            
            # Extract content
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                cleaned_line = line.lstrip('-•* ').strip()
                if current_section == 'pros' and len(pros) < 3:
                    pros.append(cleaned_line)
                elif current_section == 'cons' and len(cons) < 3:
                    cons.append(cleaned_line)
            elif current_section == 'summary' and line and not line.endswith(':'):
                summary += line + ' '
        
        # Fallback: extract from full text if parsing failed
        if not pros:
            pros = ["Overall positive feedback from customers"]
        if not cons:
            cons = ["Some minor issues reported"]
        if not summary:
            summary = text[:200] + "..." if len(text) > 200 else text
        
        return sentiment, pros[:3], cons[:3], summary.strip()

# Global instance
review_analyzer_agent = ReviewAnalyzerAgent()
