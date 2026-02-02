"""
Price Tracker API Routes

REST API endpoints for price tracking functionality

Endpoints:
- GET /api/price/track/{product_id} - Analyze price for a product
- GET /api/price/deals - Find best deals
- GET /api/price/history/{product_id} - Get price history
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.agents.price_tracker_agent import price_tracker_agent

# Create router
router = APIRouter(prefix="/api/price", tags=["Price Tracking"])


@router.get("/track/{product_id}")
async def track_product_price(product_id: int):
    """
    Track price for a specific product
    
    Args:
        product_id: ID of product to track
        
    Returns:
        Complete price analysis with AI recommendation
        
    Example:
        GET /api/price/track/2
        
        Returns:
        {
            "success": true,
            "product_name": "OnePlus Bullets 809",
            "price_data": {
                "current_price": 26192,
                "average_price": 27800,
                "min_price": 24500,
                "trend": "decreasing"
            },
            "ai_recommendation": "BUY NOW! Price at all-time low...",
            "confidence": "high"
        }
    """
    result = await price_tracker_agent.analyze_price(product_id)
    
    if not result.get('success'):
        raise HTTPException(
            status_code=404,
            detail=result.get('error', 'Product not found or no price history')
        )
    
    return result


@router.get("/deals")
async def get_best_deals(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Number of deals to return")
):
    """
    Find best deals across products
    
    Args:
        category: Filter by category (optional)
        limit: Maximum number of deals (1-50)
        
    Returns:
        List of best deals sorted by discount percentage
        Each deal includes:
        - is_flash_deal: boolean (true if urgent deal)
        - deal_type: "flash" or "regular"
        
    Example:
        GET /api/price/deals?category=Electronics&limit=5
        
        Returns top 5 electronics deals with highest discounts
    """
    result = await price_tracker_agent.find_best_deals(
        category=category,
        limit=limit
    )
    
    if not result.get('success'):
        raise HTTPException(
            status_code=500,
            detail=result.get('error', 'Failed to fetch deals')
        )
    
    return result


@router.get("/flash-deals")
async def get_flash_deals(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=20, description="Number of flash deals")
):
    """
    Find ONLY flash/blast deals (urgent deals)
    
    Flash deals are identified by:
    - Price dropped >10% in last 48 hours
    - OR price at all-time low (90 days)
    
    Args:
        category: Filter by category (optional)
        limit: Maximum number of flash deals (1-20)
        
    Returns:
        List of flash deals with urgency indicators
        
    Example:
        GET /api/price/flash-deals?limit=5
        
        Returns:
        {
            "flash_deals": [
                {
                    "product_id": 123,
                    "name": "Product Name",
                    "discount_pct": 35,
                    "is_flash_deal": true,
                    "urgency_level": "high",
                    "urgency_score": 35
                }
            ],
            "count": 5
        }
    """
    from src.tools.price_tools import price_tools
    from src.database.connection import get_db
    
    db = next(get_db())
    
    try:
        flash_deals = await price_tools.find_flash_deals(
            db=db,
            category=category,
            limit=limit
        )
        
        return {
            "success": True,
            "flash_deals": flash_deals,
            "count": len(flash_deals),
            "message": f"Found {len(flash_deals)} flash deals - Act fast!"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch flash deals: {str(e)}"
        )
    finally:
        db.close()


@router.get("/history/{product_id}")
async def get_price_history(
    product_id: int,
    days: int = Query(30, ge=7, le=365, description="Number of days of history")
):
    """
    Get price history for a product
    
    Args:
        product_id: ID of product
        days: Number of days (7-365)
        
    Returns:
        Price history data
        
    Example:
        GET /api/price/history/2?days=90
        
        Returns 90 days of price history
    """
    from src.tools.price_tools import price_tools
    from src.database.connection import get_db
    
    db = next(get_db())
    
    try:
        history = await price_tools.get_price_history(
            db=db,
            product_id=product_id,
            days=days
        )
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No price history found for product {product_id}"
            )
        
        return {
            "success": True,
            "product_id": product_id,
            "history": history,
            "count": len(history),
            "days": days
        }
        
    finally:
        db.close()


@router.get("/chart/{product_id}")
async def get_price_chart(
    product_id: int,
    days: int = Query(90, ge=7, le=365, description="Number of days of history")
):
    """
    Get enhanced price chart data with visual features
    
    Perfect for frontend charts like Chart.js, Recharts, or ApexCharts
    Includes: annotations, price zones, trend lines, key markers
    
    Args:
        product_id: ID of product
        days: Number of days (7-365)
        
    Returns:
        Rich chart data with visual enhancements
        
    Example:
        GET /api/price/chart/2?days=90
        
        Returns beautiful chart data ready for rendering
    """
    from src.tools.price_tools import price_tools
    from src.utils.price_chart_generator import price_chart_generator
    from src.database.connection import get_db
    
    db = next(get_db())
    
    try:
        # Get price history
        history = await price_tools.get_price_history(
            db=db,
            product_id=product_id,
            days=days
        )
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No price history found for product {product_id}"
            )
        
        # Generate enhanced chart data
        chart_data = price_chart_generator.generate_chart_data(history, days)
        
        if "error" in chart_data:
            raise HTTPException(
                status_code=404,
                detail=chart_data["error"]
            )
        
        return {
            "success": True,
            "product_id": product_id,
            "chart": chart_data
        }
        
    finally:
        db.close()


@router.post("/compare")
async def compare_product_prices(product_ids: list):
    """
    Compare prices across multiple products
    
    Body:
        product_ids: List of product IDs
        
    Example:
        POST /api/price/compare
        Body: {"product_ids": [1, 2, 3]}
    """
    if not product_ids or len(product_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least 2 product IDs to compare"
        )
    
    if len(product_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 products can be compared at once"
        )
    
    result = await price_tracker_agent.compare_prices(product_ids)
    
    return result
