"""
Buy Plan Optimizer Agent - AI-powered payment optimization
Helps users find the best payment options and maximize savings
"""

import os
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import ollama
import logging

from src.database.models import Product
from src.database.connection import get_db
from src.tools import buyplan_tools

logger = logging.getLogger(__name__)


class BuyPlanOptimizerAgent:
    """
    AI-powered Buy Plan Optimizer Agent
    
    Specializes in:
    - Finding best payment options
    - Calculating savings across different payment methods
    - Recommending optimal purchase plans
    - EMI plan optimization
    """
    
    def __init__(self):
        """Initialize the Buy Plan Optimizer Agent"""
        self.client = ollama
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.1')
        
        # Test Ollama connection
        try:
            self.client.list()
            print(f"Buy Plan Optimizer: Ollama connected! Using model: {self.model_name}")
        except Exception as e:
            print(f"Ollama not running. Start with: ollama serve")
            print(f"Error: {e}")
    
    async def create_purchase_plan(
        self,
        product_id: int,
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive purchase plan for a product
        
        This is the main method that:
        1. Fetches product details
        2. Gets all card offers
        3. Calculates EMI plans
        4. Compares payment options
        5. Uses AI to recommend best plan
        
        Args:
            product_id: Product ID (from search results)
            user_preference: User's payment preference (instant_savings, emi, cashback)
            
        Returns:
            Complete purchase plan with recommendations
        """
        db = next(get_db())
        
        try:
            logger.info(f"Creating purchase plan for product {product_id}")
            
            # Get complete payment comparison
            comparison = await buyplan_tools.compare_payment_options(product_id, db)
            
            if not comparison.get('success'):
                return {
                    "success": False,
                    "error": comparison.get('error', 'Failed to create purchase plan')
                }
            
            # Get product details
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return {
                    "success": False,
                    "error": "Product not found"
                }
            
            # Check EMI eligibility
            emi_eligibility = await buyplan_tools.get_emi_eligibility(float(product.price))
            
            # Generate AI recommendation
            ai_recommendation = await self._generate_ai_recommendation(
                product=product,
                comparison=comparison,
                user_preference=user_preference
            )
            
            # Build complete purchase plan
            purchase_plan = {
                "success": True,
                "product_id": product_id,
                "product_name": product.name,
                "product_price": float(product.price),
                "product_mrp": float(product.mrp) if product.mrp else float(product.price),
                "emi_eligible": emi_eligibility['eligible_for_emi'],
                "payment_options": comparison['payment_options'],
                "regular_emi_plans": comparison['regular_emi_plans'],
                "no_cost_emi_plans": comparison['no_cost_emi_plans'],
                "recommendations": {
                    "best_instant_savings": comparison['recommendations']['best_instant_savings'],
                    "best_cashback": comparison['recommendations']['best_cashback'],
                    "best_emi": comparison['recommendations']['best_emi'],
                    "ai_recommendation": ai_recommendation
                },
                "summary": self._generate_summary(comparison, ai_recommendation)
            }
            
            logger.info(f"Purchase plan created successfully for product {product_id}")
            return purchase_plan
            
        except Exception as e:
            logger.error(f"Error creating purchase plan: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def recommend_best_payment_method(
        self,
        product_id: int,
        user_cards: Optional[List[str]] = None,
        budget_preference: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Recommend the best payment method based on user's cards and preference
        
        Args:
            product_id: Product ID
            user_cards: List of banks user has cards with (e.g., ['HDFC', 'SBI'])
            budget_preference: 'instant_savings', 'emi', or 'balanced'
            
        Returns:
            Personalized payment recommendation
        """
        db = next(get_db())
        
        try:
            # Get product
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return {
                    "success": False,
                    "error": "Product not found"
                }
            
            # Get all payment options
            comparison = await buyplan_tools.compare_payment_options(product_id, db)
            
            if not comparison.get('success'):
                return comparison
            
            # Filter options based on user's cards
            available_options = comparison['payment_options']
            
            if user_cards:
                # Filter to only show options for cards user has
                available_options = [
                    opt for opt in available_options
                    if any(bank.lower() in opt['payment_method'].lower() for bank in user_cards) or 
                    opt['payment_method'] == 'Any Card/Cash'
                ]
            
            # Select best option based on preference
            recommended_option = None
            
            if budget_preference == "instant_savings":
                # Find option with highest instant savings
                instant_options = [opt for opt in available_options if opt['payment_type'] == 'one_time']
                if instant_options:
                    recommended_option = max(instant_options, key=lambda x: x.get('total_savings', 0))
            
            elif budget_preference == "emi":
                # Find best EMI option (lowest monthly payment)
                emi_options = [opt for opt in available_options if opt['payment_type'] == 'emi']
                if emi_options:
                    recommended_option = min(emi_options, key=lambda x: x.get('emi_per_month', float('inf')))
                elif comparison['no_cost_emi_plans']:
                    # Use no-cost EMI if available
                    recommended_option = {
                        "option_name": "No Cost EMI (Best for Budget)",
                        "payment_type": "emi",
                        **comparison['no_cost_emi_plans'][0]
                    }
            
            else:  # balanced
                # Highest overall savings
                if available_options:
                    recommended_option = max(available_options, key=lambda x: x.get('total_savings', 0))
            
            # Fallback to full price if no better option
            if not recommended_option:
                recommended_option = available_options[0] if available_options else None
            
            return {
                "success": True,
                "product_id": product_id,
                "product_name": product.name,
                "product_price": float(product.price),
                "user_preference": budget_preference,
                "user_cards": user_cards,
                "recommended_option": recommended_option,
                "alternative_options": available_options[:3],  # Top 3 alternatives
                "reason": self._explain_recommendation(recommended_option, budget_preference)
            }
            
        except Exception as e:
            logger.error(f"Error recommending payment method: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def _generate_ai_recommendation(
        self,
        product: Any,
        comparison: Dict[str, Any],
        user_preference: Optional[str]
    ) -> str:
        """
        Use AI to generate intelligent purchase recommendation
        
        Args:
            product: Product object
            comparison: Payment options comparison
            user_preference: User's stated preference
            
        Returns:
            AI-generated recommendation text
        """
        try:
            # Prepare context for AI
            best_options = comparison['recommendations']
            
            mrp_value = product.mrp if product.mrp else product.price
            
            prompt = f"""You are a Buy Plan Optimizer Agent helping users make smart purchase decisions.

Product: {product.name}
Price: Rs. {product.price:,.2f}
MRP: Rs. {mrp_value:,.2f}

Available Payment Options:
"""
            
            if best_options['best_instant_savings']:
                opt = best_options['best_instant_savings']
                prompt += f"\n1. INSTANT SAVINGS: {opt['option_name']}"
                prompt += f"\n   Final Price: Rs. {opt['final_price']:,.2f}"
                prompt += f"\n   You Save: Rs. {opt['additional_savings']:,.2f}"
            
            if best_options['best_cashback']:
                opt = best_options['best_cashback']
                prompt += f"\n\n2. CASHBACK: {opt['option_name']}"
                prompt += f"\n   Cashback: Rs. {opt['cashback_amount']:,.2f}"
                prompt += f"\n   Effective Price: Rs. {opt['effective_price']:,.2f}"
            
            if best_options['best_emi']:
                opt = best_options['best_emi']
                prompt += f"\n\n3. EMI: {opt['option_name']}"
                prompt += f"\n   EMI: Rs. {opt['emi_per_month']:,.2f}/month x {opt['tenure_months']} months"
            
            prompt += f"\n\nUser Preference: {user_preference or 'Not specified'}"
            
            prompt += """\n\nProvide a recommendation in 2-3 sentences. Consider:
- Maximum savings
- Payment convenience
- User preference if specified
- Time value of money (cashback takes 90 days)

Keep it conversational and helpful."""
            
            # Call Ollama for AI recommendation
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial advisor specializing in purchase optimization. Be concise and practical."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 200
                }
            )
            
            recommendation = response['message']['content'].strip()
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating AI recommendation: {str(e)}")
            return "Choose the option with highest savings based on your payment preference."
    
    def _generate_summary(
        self,
        comparison: Dict[str, Any],
        ai_recommendation: str
    ) -> str:
        """
        Generate a user-friendly summary of the purchase plan
        
        Args:
            comparison: Payment options comparison
            ai_recommendation: AI-generated recommendation
            
        Returns:
            Formatted summary text
        """
        try:
            summary = []
            summary.append("PURCHASE PLAN SUMMARY")
            summary.append("=" * 50)
            summary.append(f"\nProduct: {comparison['product_name']}")
            summary.append(f"Price: Rs. {comparison['product_price']:,.2f}")
            
            # Best options
            best = comparison['recommendations']
            
            if best['best_instant_savings']:
                opt = best['best_instant_savings']
                summary.append(f"\nBest Instant Savings:")
                summary.append(f"  {opt['option_name']}")
                summary.append(f"  Final Price: Rs. {opt['final_price']:,.2f}")
                summary.append(f"  You Save: Rs. {opt['additional_savings']:,.2f}")
            
            if best['best_cashback']:
                opt = best['best_cashback']
                summary.append(f"\nBest Cashback:")
                summary.append(f"  {opt['option_name']}")
                summary.append(f"  Cashback: Rs. {opt['cashback_amount']:,.2f}")
                summary.append(f"  (Credited in 90 days)")
            
            if best['best_emi']:
                opt = best['best_emi']
                summary.append(f"\nBest EMI Option:")
                summary.append(f"  {opt['option_name']}")
                summary.append(f"  Rs. {opt['emi_per_month']:,.2f}/month x {opt['tenure_months']} months")
            
            summary.append(f"\nRECOMMENDATION:")
            summary.append(f"  {ai_recommendation}")
            
            summary.append("\n" + "=" * 50)
            
            return "\n".join(summary)
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Purchase plan generated successfully."
    
    def _explain_recommendation(
        self,
        recommended_option: Optional[Dict[str, Any]],
        preference: str
    ) -> str:
        """
        Explain why this option was recommended
        
        Args:
            recommended_option: The recommended payment option
            preference: User's stated preference
            
        Returns:
            Explanation text
        """
        if not recommended_option:
            return "No specific recommendation available. Choose based on your preference."
        
        reasons = []
        
        if preference == "instant_savings":
            reasons.append("Maximizes immediate savings")
            if recommended_option.get('additional_savings'):
                reasons.append(f"Save Rs. {recommended_option['additional_savings']:,.2f} instantly")
        
        elif preference == "emi":
            reasons.append("Spreads payment over time")
            if recommended_option.get('emi_per_month'):
                reasons.append(f"Affordable EMI of Rs. {recommended_option['emi_per_month']:,.2f}/month")
        
        else:
            if recommended_option.get('total_savings', 0) > 0:
                reasons.append(f"Best overall value with Rs. {recommended_option.get('total_savings', 0):,.2f} total savings")
        
        if recommended_option.get('payment_type') == 'emi' and recommended_option.get('total_interest', 0) == 0:
            reasons.append("Zero interest (No Cost EMI)")
        
        return ". ".join(reasons) + "."


# Create global instance
buyplan_optimizer_agent = BuyPlanOptimizerAgent()
