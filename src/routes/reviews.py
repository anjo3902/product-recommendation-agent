# src/routes/reviews.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.agents.review_analyzer_agent import review_analyzer_agent
from typing import Dict

router = APIRouter()

@router.get("/api/reviews/analyze/{product_id}")
async def analyze_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Analyze reviews for a specific product
    
    Args:
        product_id: Product ID to analyze reviews for
        
    Returns:
        Review analysis with sentiment, pros, cons, and summary
        
    Example:
        GET /api/reviews/analyze/7
        
        Response:
        {
            "success": true,
            "product_id": 7,
            "sentiment": "Positive",
            "pros": ["Great sound quality", "Good battery life", "Water resistant"],
            "cons": ["Fit issues", "Connection drops sometimes"],
            "summary": "Overall excellent product with great sound...",
            "trust_score": 0.85,
            "statistics": {...}
        }
    """
    result = await review_analyzer_agent.analyze_reviews(product_id)
    
    if not result['success']:
        raise HTTPException(
            status_code=404 if "not found" in result.get('message', '').lower() else 500,
            detail=result.get('message') or result.get('error', 'Analysis failed')
        )
    
    return result

@router.get("/api/reviews/{product_id}")
async def get_product_reviews(
    product_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get raw reviews for a product
    
    Args:
        product_id: Product ID
        limit: Maximum number of reviews to return
        
    Returns:
        List of reviews
    """
    from src.tools.review_tools import review_tools
    
    reviews = await review_tools.get_reviews(
        db=db,
        product_id=product_id,
        limit=limit
    )
    
    stats = await review_tools.get_review_statistics(
        db=db,
        product_id=product_id
    )
    
    return {
        "success": True,
        "product_id": product_id,
        "reviews": reviews,
        "statistics": stats
    }
