"""
Buy Plan API Routes
REST API endpoints for purchase plan optimization
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import logging

from src.agents.buyplan_optimizer_agent import buyplan_optimizer_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/buyplan", tags=["buy-plan"])


class PurchasePlanRequest(BaseModel):
    """Request model for purchase plan"""
    product_id: int
    user_preference: Optional[str] = None  # instant_savings, emi, cashback, balanced


class PaymentRecommendationRequest(BaseModel):
    """Request model for personalized payment recommendation"""
    product_id: int
    user_cards: Optional[List[str]] = None  # ['HDFC', 'SBI', 'ICICI']
    budget_preference: str = "balanced"  # instant_savings, emi, balanced


@router.post("/")
async def create_purchase_plan(request: PurchasePlanRequest):
    """
    Create comprehensive purchase plan for a product
    
    This endpoint analyzes all payment options and provides:
    - Card offers (instant discounts, cashback)
    - EMI plans (regular and no-cost)
    - AI-powered recommendations
    - Savings calculations
    
    Args:
        request: Purchase plan request with product_id and user preference
        
    Returns:
        Complete purchase plan with all payment options
        
    Example:
        POST /api/buyplan/
        {
            "product_id": 123,
            "user_preference": "instant_savings"
        }
        
        Response:
        {
            "success": true,
            "product_name": "HP Laptop",
            "product_price": 58999,
            "payment_options": [...],
            "recommendations": {
                "best_instant_savings": {...},
                "best_cashback": {...},
                "best_emi": {...},
                "ai_recommendation": "..."
            }
        }
    """
    try:
        result = await buyplan_optimizer_agent.create_purchase_plan(
            product_id=request.product_id,
            user_preference=request.user_preference
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=404 if 'not found' in result.get('error', '').lower() else 400,
                detail=result.get('error', 'Failed to create purchase plan')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_purchase_plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{product_id}")
async def get_purchase_plan(
    product_id: int,
    user_preference: Optional[str] = Query(None, description="User's payment preference")
):
    """
    Get purchase plan for a product (GET alternative)
    
    Args:
        product_id: Product ID
        user_preference: Optional payment preference
        
    Returns:
        Purchase plan with payment options
        
    Example:
        GET /api/buyplan/123?user_preference=instant_savings
    """
    try:
        result = await buyplan_optimizer_agent.create_purchase_plan(
            product_id=product_id,
            user_preference=user_preference
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=404 if 'not found' in result.get('error', '').lower() else 400,
                detail=result.get('error', 'Failed to create purchase plan')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_purchase_plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/recommend")
async def recommend_payment_method(request: PaymentRecommendationRequest):
    """
    Get personalized payment method recommendation
    
    This endpoint provides a tailored recommendation based on:
    - User's available bank cards
    - Budget preference (instant savings vs EMI)
    - Best value for money
    
    Args:
        request: Payment recommendation request
        
    Returns:
        Personalized payment recommendation with reasoning
        
    Example:
        POST /api/buyplan/recommend
        {
            "product_id": 123,
            "user_cards": ["HDFC", "SBI"],
            "budget_preference": "instant_savings"
        }
        
        Response:
        {
            "success": true,
            "recommended_option": {
                "option_name": "HDFC Instant Discount",
                "final_price": 55999,
                "total_savings": 3000
            },
            "reason": "Maximizes immediate savings. Save Rs. 3,000 instantly.",
            "alternative_options": [...]
        }
    """
    try:
        result = await buyplan_optimizer_agent.recommend_best_payment_method(
            product_id=request.product_id,
            user_cards=request.user_cards,
            budget_preference=request.budget_preference
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=404 if 'not found' in result.get('error', '').lower() else 400,
                detail=result.get('error', 'Failed to generate recommendation')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in recommend_payment_method: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/offers/{product_id}")
async def get_card_offers(product_id: int):
    """
    Get all active card offers for a product
    
    Returns only the card offers without full purchase plan.
    Useful for quickly checking available discounts.
    
    Args:
        product_id: Product ID
        
    Returns:
        List of active card offers
        
    Example:
        GET /api/buyplan/offers/123
        
        Response:
        {
            "product_id": 123,
            "offers": [
                {
                    "bank_name": "HDFC",
                    "offer_type": "instant_discount",
                    "discount_amount": 3000,
                    "terms": "..."
                },
                ...
            ]
        }
    """
    try:
        from src.database.connection import get_db
        from src.tools import buyplan_tools
        
        db = next(get_db())
        
        try:
            offers = await buyplan_tools.get_card_offers(db, product_id)
            
            return {
                "success": True,
                "product_id": product_id,
                "offers_count": len(offers),
                "offers": offers
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error fetching card offers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch card offers: {str(e)}"
        )


@router.get("/emi/{product_id}")
async def get_emi_plans(
    product_id: int,
    plan_type: str = Query("both", description="EMI plan type: regular, no_cost, or both")
):
    """
    Get EMI plans for a product
    
    Returns EMI calculations for different tenures.
    
    Args:
        product_id: Product ID
        plan_type: Type of EMI plans to return (regular, no_cost, both)
        
    Returns:
        EMI plans with monthly payment calculations
        
    Example:
        GET /api/buyplan/emi/123?plan_type=no_cost
        
        Response:
        {
            "product_id": 123,
            "product_price": 58999,
            "emi_eligible": true,
            "no_cost_emi_plans": [
                {
                    "tenure_months": 6,
                    "emi_per_month": 9833.17,
                    "total_amount": 58999,
                    "total_interest": 0
                },
                ...
            ]
        }
    """
    try:
        from src.database.connection import get_db
        from src.database.models import Product
        from src.tools import buyplan_tools
        
        db = next(get_db())
        
        try:
            # Get product
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            product_price = float(product.price)
            
            # Check EMI eligibility
            eligibility = await buyplan_tools.get_emi_eligibility(product_price)
            
            result = {
                "success": True,
                "product_id": product_id,
                "product_name": product.name,
                "product_price": product_price,
                "emi_eligible": eligibility['eligible_for_emi']
            }
            
            if not eligibility['eligible_for_emi']:
                result['message'] = eligibility['message']
                return result
            
            # Calculate EMI plans based on type requested
            if plan_type in ["regular", "both"]:
                regular_emi = await buyplan_tools.calculate_emi_plans(product_price)
                result['regular_emi_plans'] = regular_emi
            
            if plan_type in ["no_cost", "both"]:
                no_cost_emi = await buyplan_tools.calculate_no_cost_emi(product_price)
                result['no_cost_emi_plans'] = no_cost_emi
            
            return result
            
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching EMI plans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EMI plans: {str(e)}"
        )


@router.get("/savings/{product_id}")
async def calculate_savings(product_id: int):
    """
    Calculate total savings for all payment options
    
    Compares all payment methods and shows potential savings.
    
    Args:
        product_id: Product ID
        
    Returns:
        All payment options sorted by total savings
        
    Example:
        GET /api/buyplan/savings/123
        
        Response:
        {
            "product_id": 123,
            "payment_options": [
                {
                    "option_name": "HDFC Instant Discount",
                    "final_price": 55999,
                    "total_savings": 6000,
                    "savings_percent": 9.23
                },
                ...
            ]
        }
    """
    try:
        from src.database.connection import get_db
        from src.tools import buyplan_tools
        
        db = next(get_db())
        
        try:
            comparison = await buyplan_tools.compare_payment_options(product_id, db)
            
            if not comparison.get('success'):
                raise HTTPException(
                    status_code=404 if 'not found' in comparison.get('error', '').lower() else 400,
                    detail=comparison.get('error', 'Failed to calculate savings')
                )
            
            return {
                "success": True,
                "product_id": product_id,
                "product_name": comparison['product_name'],
                "product_price": comparison['product_price'],
                "product_mrp": comparison['product_mrp'],
                "payment_options": comparison['payment_options'],
                "best_savings": comparison['payment_options'][0] if comparison['payment_options'] else None
            }
            
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating savings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate savings: {str(e)}"
        )
