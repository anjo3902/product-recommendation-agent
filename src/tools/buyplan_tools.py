"""
Buy Plan Tools - Fetching card offers and EMI calculations
Tools for the Buy Plan Optimizer Agent
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import logging

from src.database.models import Product, CardOffer

logger = logging.getLogger(__name__)


async def get_card_offers(
    db: Session,
    product_id: int
) -> List[Dict[str, Any]]:
    """
    Fetch all active card offers for a product
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        List of active card offers
    """
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            logger.warning(f"Product {product_id} not found")
            return []
        
        # Get all card offers for this product
        offers = db.query(CardOffer).filter(
            CardOffer.product_id == product_id
        ).all()
        
        if not offers:
            logger.info(f"No card offers found for product {product_id}")
            return []
        
        # Format offers
        formatted_offers = []
        for offer in offers:
            offer_data = {
                "id": offer.id,
                "bank_name": offer.bank_name,
                "offer_type": offer.offer_type,  # instant_discount, cashback, no_cost_emi
                "discount_percent": float(offer.discount_percentage) if offer.discount_percentage else None,
                "discount_amount": float(offer.discount_amount) if offer.discount_amount else None,
                "cashback_amount": float(offer.cashback_amount) if offer.cashback_amount else None,
                "emi_months": int(offer.emi_tenure) if offer.emi_tenure and offer.emi_tenure.isdigit() else None,
                "emi_amount": None,  # Will be calculated if needed
                "min_purchase": float(offer.min_transaction_amount) if offer.min_transaction_amount else None,
                "max_discount": None,  # Not in current model
                "valid_from": offer.valid_from.isoformat() if offer.valid_from else None,
                "valid_till": offer.valid_till.isoformat() if offer.valid_till else None,
                "terms": offer.offer_description
            }
            formatted_offers.append(offer_data)
        
        logger.info(f"Found {len(formatted_offers)} card offers for product {product_id}")
        return formatted_offers
        
    except Exception as e:
        logger.error(f"Error fetching card offers: {str(e)}")
        return []


async def calculate_emi_plans(
    price: float,
    tenures: List[int] = [3, 6, 9, 12, 18, 24]
) -> List[Dict[str, Any]]:
    """
    Calculate EMI plans for different tenures
    
    Args:
        price: Product price
        tenures: List of EMI tenure months (default: 3, 6, 9, 12, 18, 24)
        
    Returns:
        List of EMI plans with calculations
    """
    try:
        emi_plans = []
        
        # Standard interest rates for regular EMI
        interest_rates = {
            3: 12.0,   # 12% annual for 3 months
            6: 13.0,   # 13% annual for 6 months
            9: 14.0,   # 14% annual for 9 months
            12: 15.0,  # 15% annual for 12 months
            18: 16.0,  # 16% annual for 18 months
            24: 17.0   # 17% annual for 24 months
        }
        
        for months in tenures:
            # Get interest rate for this tenure
            annual_rate = interest_rates.get(months, 15.0)
            monthly_rate = annual_rate / 12 / 100
            
            # Calculate EMI using formula: P * r * (1+r)^n / ((1+r)^n - 1)
            if monthly_rate > 0:
                emi_amount = (price * monthly_rate * ((1 + monthly_rate) ** months)) / \
                             (((1 + monthly_rate) ** months) - 1)
            else:
                emi_amount = price / months
            
            total_amount = emi_amount * months
            total_interest = total_amount - price
            
            emi_plans.append({
                "tenure_months": months,
                "emi_per_month": round(emi_amount, 2),
                "total_amount": round(total_amount, 2),
                "total_interest": round(total_interest, 2),
                "interest_rate_annual": annual_rate,
                "processing_fee": 199.0,  # Standard processing fee
                "plan_type": "regular_emi"
            })
        
        return emi_plans
        
    except Exception as e:
        logger.error(f"Error calculating EMI plans: {str(e)}")
        return []


async def calculate_no_cost_emi(
    price: float,
    tenures: List[int] = [3, 6, 9, 12]
) -> List[Dict[str, Any]]:
    """
    Calculate No Cost EMI plans (interest absorbed by merchant)
    
    Args:
        price: Product price
        tenures: List of available no-cost EMI tenures
        
    Returns:
        List of No Cost EMI plans
    """
    try:
        no_cost_plans = []
        
        for months in tenures:
            # No cost EMI: Total = Price (no interest)
            emi_amount = price / months
            processing_fee = 199.0
            
            no_cost_plans.append({
                "tenure_months": months,
                "emi_per_month": round(emi_amount, 2),
                "total_amount": round(price, 2),
                "total_interest": 0.0,
                "interest_rate_annual": 0.0,
                "processing_fee": processing_fee,
                "plan_type": "no_cost_emi",
                "total_payable": round(price + processing_fee, 2)
            })
        
        return no_cost_plans
        
    except Exception as e:
        logger.error(f"Error calculating no-cost EMI: {str(e)}")
        return []


async def calculate_total_savings(
    product_price: float,
    product_mrp: float,
    offers: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Calculate total savings for each payment option
    
    Args:
        product_price: Current selling price
        product_mrp: Maximum Retail Price (original price)
        offers: List of card offers
        
    Returns:
        List of payment options with savings
    """
    try:
        payment_options = []
        
        # Base discount (current price vs MRP)
        base_discount = product_mrp - product_price if product_mrp else 0
        
        # Option 1: Pay full price (no offers)
        payment_options.append({
            "option_name": "Full Price Payment",
            "payment_method": "Any Card/Cash",
            "final_price": product_price,
            "discount_from_mrp": base_discount,
            "additional_savings": 0,
            "total_savings": base_discount,
            "savings_percent": round((base_discount / product_mrp * 100), 2) if product_mrp else 0,
            "payment_type": "one_time"
        })
        
        # Option 2-N: Card offers
        for offer in offers:
            final_price = product_price
            additional_savings = 0
            
            if offer['offer_type'] == 'instant_discount':
                if offer['discount_amount']:
                    additional_savings = offer['discount_amount']
                elif offer['discount_percent']:
                    additional_savings = product_price * (offer['discount_percent'] / 100)
                    # Apply max discount cap if exists
                    if offer['max_discount']:
                        additional_savings = min(additional_savings, offer['max_discount'])
                
                final_price = product_price - additional_savings
                
                payment_options.append({
                    "option_name": f"{offer['bank_name']} Instant Discount",
                    "payment_method": f"{offer['bank_name']} Card",
                    "final_price": round(final_price, 2),
                    "discount_from_mrp": base_discount,
                    "additional_savings": round(additional_savings, 2),
                    "total_savings": round(base_discount + additional_savings, 2),
                    "savings_percent": round(((base_discount + additional_savings) / product_mrp * 100), 2) if product_mrp else 0,
                    "payment_type": "one_time",
                    "offer_details": offer['terms']
                })
            
            elif offer['offer_type'] == 'cashback':
                cashback = offer['cashback_amount'] or 0
                
                payment_options.append({
                    "option_name": f"{offer['bank_name']} Cashback",
                    "payment_method": f"{offer['bank_name']} Card",
                    "final_price": product_price,  # Pay full price upfront
                    "cashback_amount": round(cashback, 2),
                    "effective_price": round(product_price - cashback, 2),
                    "discount_from_mrp": base_discount,
                    "additional_savings": round(cashback, 2),
                    "total_savings": round(base_discount + cashback, 2),
                    "savings_percent": round(((base_discount + cashback) / product_mrp * 100), 2) if product_mrp else 0,
                    "payment_type": "cashback",
                    "cashback_credit_days": 90,  # Typically 90 days
                    "offer_details": offer['terms']
                })
            
            elif offer['offer_type'] == 'no_cost_emi':
                if offer['emi_months'] and offer['emi_amount']:
                    payment_options.append({
                        "option_name": f"{offer['bank_name']} No Cost EMI",
                        "payment_method": f"{offer['bank_name']} Card",
                        "emi_per_month": round(offer['emi_amount'], 2),
                        "tenure_months": offer['emi_months'],
                        "total_amount": round(offer['emi_amount'] * offer['emi_months'], 2),
                        "processing_fee": 199.0,
                        "total_interest": 0,
                        "discount_from_mrp": base_discount,
                        "total_savings": base_discount,
                        "savings_percent": round((base_discount / product_mrp * 100), 2) if product_mrp else 0,
                        "payment_type": "emi",
                        "offer_details": offer['terms']
                    })
        
        # Sort by total savings (highest first)
        payment_options.sort(key=lambda x: x.get('total_savings', 0), reverse=True)
        
        return payment_options
        
    except Exception as e:
        logger.error(f"Error calculating savings: {str(e)}")
        return []


async def compare_payment_options(
    product_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Compare all available payment options for a product
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        Complete comparison of payment options
    """
    try:
        # Get product details
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return {
                "success": False,
                "error": "Product not found"
            }
        
        # Get card offers
        card_offers = await get_card_offers(db, product_id)
        
        # Calculate regular EMI plans
        regular_emi = await calculate_emi_plans(float(product.price))
        
        # Calculate no-cost EMI plans
        no_cost_emi = await calculate_no_cost_emi(float(product.price))
        
        # Calculate savings for each option
        payment_options = await calculate_total_savings(
            product_price=float(product.price),
            product_mrp=float(product.mrp) if product.mrp else float(product.price),
            offers=card_offers
        )
        
        # Find best options
        best_instant_savings = None
        best_cashback = None
        best_emi = None
        
        for option in payment_options:
            if option['payment_type'] == 'one_time' and 'Instant Discount' in option['option_name']:
                if not best_instant_savings or option['total_savings'] > best_instant_savings['total_savings']:
                    best_instant_savings = option
            
            elif option['payment_type'] == 'cashback':
                if not best_cashback or option['total_savings'] > best_cashback['total_savings']:
                    best_cashback = option
            
            elif option['payment_type'] == 'emi':
                if not best_emi or option['emi_per_month'] < best_emi['emi_per_month']:
                    best_emi = option
        
        return {
            "success": True,
            "product_id": product_id,
            "product_name": product.name,
            "product_price": float(product.price),
            "product_mrp": float(product.mrp) if product.mrp else float(product.price),
            "payment_options": payment_options,
            "regular_emi_plans": regular_emi,
            "no_cost_emi_plans": no_cost_emi,
            "recommendations": {
                "best_instant_savings": best_instant_savings,
                "best_cashback": best_cashback,
                "best_emi": best_emi
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing payment options: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_emi_eligibility(
    product_price: float,
    min_purchase_amount: float = 5000.0
) -> Dict[str, Any]:
    """
    Check EMI eligibility for a product
    
    Args:
        product_price: Product price
        min_purchase_amount: Minimum amount for EMI (default: Rs. 5,000)
        
    Returns:
        EMI eligibility information
    """
    try:
        is_eligible = product_price >= min_purchase_amount
        
        return {
            "eligible_for_emi": is_eligible,
            "product_price": product_price,
            "minimum_amount_required": min_purchase_amount,
            "message": "Eligible for EMI" if is_eligible else f"EMI available for purchases above Rs. {min_purchase_amount:,.0f}"
        }
        
    except Exception as e:
        logger.error(f"Error checking EMI eligibility: {str(e)}")
        return {
            "eligible_for_emi": False,
            "error": str(e)
        }
