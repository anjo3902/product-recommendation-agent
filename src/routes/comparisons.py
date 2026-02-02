"""
Comparison API Routes
REST API endpoints for product comparisons
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from src.agents.comparison_agent import comparison_agent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/compare", tags=["comparisons"])


class ComparisonRequest(BaseModel):
    """Request model for product comparison"""
    product_ids: List[int]
    style: Optional[str] = "detailed"  # table, battle, winner, detailed, use_case


class WinnerRequest(BaseModel):
    """Request model for winner recommendation"""
    product_ids: List[int]
    use_case: Optional[str] = None


class SearchAndCompareRequest(BaseModel):
    """Request model for search + compare workflow"""
    search_query: str
    top_n: Optional[int] = 3
    comparison_style: Optional[str] = "detailed"


@router.post("/")
async def compare_products(request: ComparisonRequest):
    """
    Compare multiple products
    
    Args:
        request: Comparison request with product IDs and style
        
    Returns:
        Comprehensive comparison with AI analysis
        
    Example:
        POST /api/compare
        {
            "product_ids": [1, 2, 3],
            "style": "detailed"
        }
        
        Styles:
        - table: Side-by-side grid comparison
        - battle: Round-by-round (requires 2 products)
        - winner: Direct recommendation
        - detailed: Full analysis with AI
        - use_case: Best for specific needs
    """
    try:
        # Validate style
        valid_styles = ["table", "battle", "winner", "detailed", "use_case"]
        if request.style not in valid_styles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}"
            )
        
        # Perform comparison
        result = await comparison_agent.compare_products(
            product_ids=request.product_ids,
            comparison_style=request.style
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Comparison failed')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/")
async def compare_products_get(
    product_ids: str = Query(..., description="Comma-separated product IDs (e.g., '1,2,3')"),
    style: str = Query("detailed", description="Comparison style: table, battle, winner, detailed, use_case")
):
    """
    Compare products via GET request
    
    Args:
        product_ids: Comma-separated product IDs
        style: Comparison style
        
    Returns:
        Comparison results
        
    Example:
        GET /api/compare?product_ids=1,2,3&style=table
    """
    try:
        # Parse product IDs
        ids = [int(id.strip()) for id in product_ids.split(',')]
        
        if len(ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 product IDs"
            )
        
        if len(ids) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 products can be compared"
            )
        
        # Perform comparison
        result = await comparison_agent.compare_products(
            product_ids=ids,
            comparison_style=style
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Comparison failed')
            )
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid product IDs format. Use comma-separated integers (e.g., '1,2,3')"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison GET API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/winner")
async def get_winner(request: WinnerRequest):
    """
    Get direct winner recommendation
    
    Args:
        request: Winner request with product IDs and optional use case
        
    Returns:
        Winner recommendation with reasoning
        
    Example:
        POST /api/compare/winner
        {
            "product_ids": [1, 2, 3],
            "use_case": "gaming"
        }
        
        Use cases:
        - "budget" / "cheap": Cheapest option
        - "quality" / "best": Highest rated
        - "gaming": Best for gaming
        - null: Best overall value
    """
    try:
        result = await comparison_agent.get_winner_recommendation(
            product_ids=request.product_ids,
            use_case=request.use_case
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Winner selection failed')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Winner API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/battle/{product_id1}/{product_id2}")
async def battle_compare(product_id1: int, product_id2: int):
    """
    Battle-style comparison between two products
    
    Args:
        product_id1: First product ID
        product_id2: Second product ID
        
    Returns:
        Battle-style comparison (round-by-round)
        
    Example:
        GET /api/compare/battle/1/2
    """
    try:
        result = await comparison_agent.compare_products(
            product_ids=[product_id1, product_id2],
            comparison_style="battle"
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Battle comparison failed')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Battle API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/table")
async def table_compare(
    product_ids: str = Query(..., description="Comma-separated product IDs"),
    attributes: Optional[str] = Query(None, description="Comma-separated attributes to compare")
):
    """
    Table-style comparison
    
    Args:
        product_ids: Comma-separated product IDs
        attributes: Optional comma-separated attributes
        
    Returns:
        Table comparison
        
    Example:
        GET /api/compare/table?product_ids=1,2,3&attributes=price,rating,discount_pct
    """
    try:
        # Parse product IDs
        ids = [int(id.strip()) for id in product_ids.split(',')]
        
        result = await comparison_agent.compare_products(
            product_ids=ids,
            comparison_style="table"
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Table comparison failed')
            )
        
        return result
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid product IDs format"
        )
    except HTTPException:
        raise


@router.post("/search-and-compare")
async def search_and_compare(request: SearchAndCompareRequest):
    """
    Integrated workflow: Search for products and compare top results
    
    This endpoint combines Product Search + Comparison in one call:
    1. Searches for products matching the query
    2. Takes top N results (default 3)
    3. Compares them automatically
    4. Returns winner recommendation
    
    Args:
        request: Search query, top_n (2-5), comparison_style
        
    Returns:
        - Search results
        - Comparison analysis
        - Winner recommendation
        - User-friendly summary
        
    Example:
        POST /api/compare/search-and-compare
        {
            "search_query": "wireless headphones under 5000",
            "top_n": 3,
            "comparison_style": "detailed"
        }
        
    Workflow:
        User → "Find best wireless headphones"
        System → Searches → Compares top 3 → Declares winner
        User → Makes informed decision
    """
    try:
        # Validate top_n
        if request.top_n < 2 or request.top_n > 5:
            raise HTTPException(
                status_code=400,
                detail="top_n must be between 2 and 5"
            )
        
        result = await comparison_agent.compare_search_results(
            search_query=request.search_query,
            top_n=request.top_n,
            comparison_style=request.comparison_style
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Search and compare failed')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Table API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
