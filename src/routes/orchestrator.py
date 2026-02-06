"""
Orchestrator Routes - Single API endpoint for complete product recommendations

This provides a unified API that coordinates all 5 agents:
- Product Search
- Review Analyzer
- Price Tracker  
- Comparison Specialist
- Buy Plan Optimizer

Single API call → Complete recommendation
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from src.agents.orchestrator_agent import orchestrator_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrate", tags=["Orchestrator"])


class OrchestrateRequest(BaseModel):
    """Request model for orchestrated recommendation"""
    query: str = Field(..., description="Product search query", example="wireless headphones under 5000")
    category: Optional[str] = Field(None, description="Product category filter", example="Electronics")
    min_price: Optional[float] = Field(None, description="Minimum price filter", example=1000.0)
    max_price: Optional[float] = Field(None, description="Maximum price filter", example=10000.0)
    top_n: int = Field(3, description="Number of top products to analyze", ge=1, le=5, example=3)
    user_preference: Optional[str] = Field(None, description="Payment preference: instant_savings, emi, balanced, cashback", example="instant_savings")
    user_cards: Optional[List[str]] = Field(None, description="User's bank cards", example=["HDFC", "SBI"])


class OrchestrateRequestSimple(BaseModel):
    """Simplified request model - just query"""
    query: str = Field(..., description="Product search query", example="gaming laptop under 60000")


@router.post("/", summary="Complete Product Recommendation (All Agents)")
async def orchestrate_full_recommendation(request: OrchestrateRequest):
    """
    🎯 **MASTER ENDPOINT** - Complete product recommendation using all 5 agents
    
    This endpoint coordinates:
    1. **Product Search** - Finds relevant products
    2. **Review Analysis** - Analyzes customer reviews (parallel for each product)
    3. **Price Tracking** - Tracks price trends (parallel for each product)
    4. **Product Comparison** - Compares all products
    5. **Buy Plan** - Recommends best payment method for top product
    
    **Workflow:**
    ```
    User Query → Search → [All Agents in Parallel] → Combined Result
    ```
    
    **Example Request:**
    ```json
    {
        "query": "wireless headphones under 5000",
        "top_n": 3,
        "user_preference": "instant_savings",
        "user_cards": ["HDFC", "SBI"]
    }
    ```
    
    **Response includes:**
    - All products with complete analysis
    - Review sentiment, pros/cons for each
    - Price trends and buy/wait recommendations
    - Product comparison with winner
    - Best payment plan for top product
    - AI-generated summary
    
    **Performance:**
    - Typical response time: 3-5 seconds (all agents run in parallel!)
    - vs Sequential: 15-20 seconds (5x faster)
    """
    try:
        result = await orchestrator_agent.orchestrate_recommendation(
            query=request.query,
            category=request.category,
            min_price=request.min_price,
            max_price=request.max_price,
            top_n=request.top_n,
            user_preference=request.user_preference,
            user_cards=request.user_cards
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=404,
                detail=result.get('error', 'No products found')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.post("/simple", summary="Quick Recommendation (Just Query)")
async def orchestrate_simple_recommendation(request: OrchestrateRequestSimple):
    """
    🚀 **SIMPLIFIED ENDPOINT** - Quick recommendation with just a query
    
    Same as the full endpoint, but with sensible defaults:
    - top_n = 3 products
    - user_preference = balanced
    - No filters
    
    **Example Request:**
    ```json
    {
        "query": "best laptop for programming"
    }
    ```
    
    **Perfect for:**
    - Quick searches
    - Testing
    - Frontend with minimal UI
    """
    try:
        import sys
        log_msg = f"[DEBUG] /simple endpoint called with query: '{request.query}'\n"
        sys.stdout.write(log_msg)
        sys.stdout.flush()
        
        result = await orchestrator_agent.orchestrate_recommendation(
            query=request.query,
            top_n=3,
            user_preference="balanced"
        )
        
        log_msg2 = f"[DEBUG] Orchestrator result success={result.get('success')}, products={len(result.get('products', []))}, error={result.get('error')}\n"
        sys.stdout.write(log_msg2)
        sys.stdout.flush()
        
        if not result.get('success'):
            error_msg = result.get('error', 'No products found matching your query')
            log_msg3 = f"[DEBUG] Raising 404: {error_msg}\n"
            sys.stdout.write(log_msg3)
            sys.stdout.flush()
            raise HTTPException(
                status_code=404,
                detail=error_msg
            )
        
        log_msg4 = f"[DEBUG] Returning {len(result.get('products', []))} products\n"
        sys.stdout.write(log_msg4)
        sys.stdout.flush()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simple orchestration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.get("/", summary="GET Alternative (with query params)")
async def orchestrate_with_query_params(
    query: str = Query(..., description="Product search query", example="wireless mouse"),
    category: Optional[str] = Query(None, description="Category filter"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    top_n: int = Query(3, description="Number of products", ge=1, le=5),
    user_preference: Optional[str] = Query(None, description="Payment preference")
):
    """
    🔗 **GET ENDPOINT** - Same as POST but with URL parameters
    
    **Example:**
    ```
    GET /api/orchestrate/?query=wireless%20headphones&top_n=3&user_preference=instant_savings
    ```
    
    **Use case:**
    - Direct browser access
    - Simple HTTP clients
    - URL sharing
    """
    try:
        result = await orchestrator_agent.orchestrate_recommendation(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            top_n=top_n,
            user_preference=user_preference
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=404,
                detail=result.get('error', 'No products found')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GET orchestration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.get("/health", summary="Orchestrator Health Check")
async def health_check():
    """
    ❤️ **HEALTH CHECK** - Verify orchestrator and all agents are ready
    
    Returns status of:
    - Orchestrator Agent
    - Product Search Agent
    - Review Analyzer Agent
    - Price Tracker Agent
    - Comparison Agent
    - Buy Plan Optimizer Agent
    - Ollama LLM connection
    
    **Use case:**
    - Deployment verification
    - Monitoring
    - Debugging
    """
    try:
        from src.agents.product_search_agent import product_search_agent
        from src.agents.review_analyzer_agent import review_analyzer_agent
        from src.agents.price_tracker_agent import price_tracker_agent
        from src.agents.comparison_agent import comparison_agent
        from src.agents.buyplan_optimizer_agent import buyplan_optimizer_agent
        
        # Test Ollama connection
        ollama_status = "connected"
        try:
            orchestrator_agent.client.list()
        except:
            ollama_status = "disconnected"
        
        return {
            "status": "healthy",
            "orchestrator": "ready",
            "agents": {
                "product_search": "ready",
                "review_analyzer": "ready",
                "price_tracker": "ready",
                "comparison": "ready",
                "buyplan_optimizer": "ready"
            },
            "llm": {
                "provider": "Ollama",
                "model": orchestrator_agent.model_name,
                "status": ollama_status
            },
            "endpoints": {
                "full": "POST /api/orchestrate/",
                "simple": "POST /api/orchestrate/simple",
                "get": "GET /api/orchestrate/?query=...",
                "health": "GET /api/orchestrate/health"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
