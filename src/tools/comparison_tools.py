"""
Comparison Tools - Product Comparison Logic
Handles fetching products and calculating differences for comparisons
"""

from sqlalchemy.orm import Session
from src.database.models import Product, Review
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ComparisonTools:
    """Tools for product comparison operations"""
    
    async def get_products_for_comparison(
        self,
        db: Session,
        product_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple products for comparison
        
        Args:
            db: Database session
            product_ids: List of product IDs to compare
            
        Returns:
            List of product details
        """
        try:
            products = db.query(Product).filter(
                Product.id.in_(product_ids)
            ).all()
            
            if not products:
                return []
            
            # Enrich with details
            enriched_products = []
            for product in products:
                # Get specifications
                specs = product.specifications if hasattr(product, 'specifications') else {}
                
                # Parse specifications if string
                if isinstance(specs, str):
                    try:
                        import json
                        specs = json.loads(specs)
                    except:
                        specs = {}
                
                enriched_products.append({
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "model": product.model,
                    "category": product.category,
                    "subcategory": product.subcategory,
                    "price": float(product.price),
                    "mrp": float(product.mrp) if product.mrp else None,
                    "discount_pct": round(((product.mrp - product.price) / product.mrp * 100), 2) if product.mrp else 0,
                    "rating": float(product.rating),
                    "review_count": product.review_count,
                    "in_stock": product.in_stock,
                    "description": product.description,
                    "specifications": specs,
                    "features": product.features.split(',') if product.features else []
                })
            
            return enriched_products
            
        except Exception as e:
            logger.error(f"Error fetching products for comparison: {e}")
            return []
    
    async def calculate_differences(
        self,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate key differences between products
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Comparison analysis with differences
        """
        if len(products) < 2:
            return {"error": "Need at least 2 products to compare"}
        
        # Price comparison
        prices = [p['price'] for p in products]
        price_analysis = {
            "cheapest": min(prices),
            "most_expensive": max(prices),
            "price_difference": max(prices) - min(prices),
            "cheapest_product": next(p['name'] for p in products if p['price'] == min(prices)),
            "expensive_product": next(p['name'] for p in products if p['price'] == max(prices))
        }
        
        # Rating comparison
        ratings = [p['rating'] for p in products]
        rating_analysis = {
            "highest_rated": max(ratings),
            "lowest_rated": min(ratings),
            "best_product": next(p['name'] for p in products if p['rating'] == max(ratings)),
            "worst_product": next(p['name'] for p in products if p['rating'] == min(ratings))
        }
        
        # Discount comparison
        discounts = [p['discount_pct'] for p in products]
        discount_analysis = {
            "best_discount": max(discounts),
            "worst_discount": min(discounts),
            "best_deal_product": next(p['name'] for p in products if p['discount_pct'] == max(discounts))
        }
        
        # Specification comparison (key specs)
        spec_comparison = {}
        all_spec_keys = set()
        
        # Collect all specification keys
        for product in products:
            if product.get('specifications'):
                all_spec_keys.update(product['specifications'].keys())
        
        # Compare each specification
        for key in all_spec_keys:
            spec_comparison[key] = {}
            for product in products:
                spec_value = product.get('specifications', {}).get(key, 'N/A')
                spec_comparison[key][product['name']] = spec_value
        
        return {
            "price_analysis": price_analysis,
            "rating_analysis": rating_analysis,
            "discount_analysis": discount_analysis,
            "specification_comparison": spec_comparison,
            "product_count": len(products)
        }
    
    async def determine_winners(
        self,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Determine winner in each category
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Winners for each category
        """
        winners = {}
        
        # Best Price (cheapest)
        cheapest = min(products, key=lambda p: p['price'])
        winners['best_price'] = {
            "product": cheapest['name'],
            "value": f"₹{cheapest['price']:,.0f}",
            "reason": "Lowest price"
        }
        
        # Best Value (considering discount and price)
        best_value = max(products, key=lambda p: p['discount_pct'])
        winners['best_value'] = {
            "product": best_value['name'],
            "value": f"{best_value['discount_pct']}% OFF",
            "reason": f"Save ₹{(best_value['mrp'] - best_value['price']) if best_value['mrp'] else 0:,.0f}"
        }
        
        # Best Rating
        highest_rated = max(products, key=lambda p: p['rating'])
        winners['best_rating'] = {
            "product": highest_rated['name'],
            "value": f"{highest_rated['rating']}/5",
            "reason": f"{highest_rated['review_count']} reviews"
        }
        
        # Most Popular (by review count)
        most_reviewed = max(products, key=lambda p: p['review_count'])
        winners['most_popular'] = {
            "product": most_reviewed['name'],
            "value": f"{most_reviewed['review_count']} reviews",
            "reason": "Most user feedback"
        }
        
        # Best Overall (rating * review_count / price)
        for product in products:
            product['value_score'] = (product['rating'] * product['review_count']) / (product['price'] / 1000)
        
        best_overall = max(products, key=lambda p: p['value_score'])
        winners['best_overall'] = {
            "product": best_overall['name'],
            "value": f"Score: {best_overall['value_score']:.2f}",
            "reason": "Best combination of price, rating, and popularity"
        }
        
        return winners
    
    async def generate_frontend_table_data(
        self,
        products: List[Dict[str, Any]],
        attributes: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate frontend-ready comparison table data
        
        Returns structured data that can be used with any frontend
        table library (Material-UI, Ant Design, Bootstrap Table, etc.)
        
        Args:
            products: List of product dictionaries
            attributes: Specific attributes to compare (optional)
            
        Returns:
            Dictionary with table data:
            {
                "columns": [{"key": "attribute", "label": "Feature"}, ...],
                "rows": [{"attribute": "Price", "product_1": "₹2,199", ...}],
                "metadata": {"total_products": 3, "attributes_compared": 5}
            }
        """
        if not attributes:
            attributes = ['price', 'rating', 'discount_pct', 'review_count', 'in_stock']
        
        # Build columns
        columns = [
            {"key": "attribute", "label": "Feature", "width": 150}
        ]
        
        for idx, product in enumerate(products, 1):
            columns.append({
                "key": f"product_{idx}",
                "label": product['name'][:30],  # Truncate long names
                "width": 200,
                "product_id": product['id']
            })
        
        # Build rows
        rows = []
        attribute_labels = {
            'price': 'Price',
            'rating': 'Rating',
            'discount_pct': 'Discount',
            'review_count': 'Total Reviews',
            'in_stock': 'Availability',
            'brand': 'Brand',
            'model': 'Model',
            'category': 'Category'
        }
        
        for attr in attributes:
            row = {
                "attribute": attribute_labels.get(attr, attr.replace('_', ' ').title()),
                "attribute_key": attr
            }
            
            for idx, product in enumerate(products, 1):
                value = product.get(attr, 'N/A')
                
                # Format values with styling hints
                if attr == 'price':
                    row[f"product_{idx}"] = {
                        "value": f"₹{value:,.0f}" if isinstance(value, (int, float)) else str(value),
                        "raw": value,
                        "style": "currency"
                    }
                elif attr == 'rating':
                    row[f"product_{idx}"] = {
                        "value": f"{value}/5" if isinstance(value, (int, float)) else str(value),
                        "raw": value,
                        "style": "rating",
                        "color": "green" if value >= 4.0 else "orange" if value >= 3.0 else "red"
                    }
                elif attr == 'discount_pct':
                    row[f"product_{idx}"] = {
                        "value": f"{value}% OFF" if isinstance(value, (int, float)) and value > 0 else "No discount",
                        "raw": value,
                        "style": "badge",
                        "color": "green" if value >= 20 else "blue" if value > 0 else "gray"
                    }
                elif attr == 'in_stock':
                    row[f"product_{idx}"] = {
                        "value": "In Stock" if value else "Out of Stock",
                        "raw": value,
                        "style": "status",
                        "color": "green" if value else "red"
                    }
                else:
                    row[f"product_{idx}"] = {
                        "value": str(value),
                        "raw": value,
                        "style": "text"
                    }
            
            rows.append(row)
        
        # Add winner highlights
        winners = await self.determine_winners(products)
        
        return {
            "columns": columns,
            "rows": rows,
            "winners": winners,
            "metadata": {
                "total_products": len(products),
                "attributes_compared": len(attributes),
                "generated_at": datetime.utcnow().isoformat()
            },
            "recommendations": {
                "best_value": winners.get('best_value', {}).get('product'),
                "best_price": winners.get('best_price', {}).get('product'),
                "best_rating": winners.get('best_rating', {}).get('product')
            }
        }
    
    async def generate_comparison_table(
        self,
        products: List[Dict[str, Any]],
        attributes: List[str] = None
    ) -> str:
        """
        Generate ASCII comparison table (for terminal/console display)
        
        Args:
            products: List of product dictionaries
            attributes: Specific attributes to compare (optional)
            
        Returns:
            Formatted ASCII table
        """
        if not attributes:
            attributes = ['price', 'rating', 'discount_pct', 'review_count', 'in_stock']
        
        # Build table header
        product_names = [p['name'][:20] for p in products]  # Truncate long names
        header = f"{'Attribute':<20} | " + " | ".join(f"{name:^20}" for name in product_names)
        separator = "-" * len(header)
        
        table = [separator, header, separator]
        
        # Add rows for each attribute
        attribute_labels = {
            'price': 'Price',
            'rating': 'Rating',
            'discount_pct': 'Discount',
            'review_count': 'Reviews',
            'in_stock': 'In Stock',
            'brand': 'Brand',
            'model': 'Model'
        }
        
        for attr in attributes:
            label = attribute_labels.get(attr, attr.replace('_', ' ').title())
            values = []
            
            for product in products:
                value = product.get(attr, 'N/A')
                
                # Format values
                if attr == 'price':
                    formatted = f"₹{value:,.0f}" if isinstance(value, (int, float)) else str(value)
                elif attr == 'rating':
                    formatted = f"{value}/5" if isinstance(value, (int, float)) else str(value)
                elif attr == 'discount_pct':
                    formatted = f"{value}% OFF" if isinstance(value, (int, float)) and value > 0 else "No discount"
                elif attr == 'in_stock':
                    formatted = "✓ Yes" if value else "✗ No"
                else:
                    formatted = str(value)
                
                values.append(f"{formatted:^20}")
            
            row = f"{label:<20} | " + " | ".join(values)
            table.append(row)
        
        table.append(separator)
        
        return "\n".join(table)
    
    async def generate_battle_comparison(
        self,
        products: List[Dict[str, Any]]
    ) -> str:
        """
        Generate battle-style comparison (round by round)
        
        Args:
            products: List of product dictionaries (should be 2 products)
            
        Returns:
            Battle-style comparison text
        """
        if len(products) != 2:
            return "Battle mode requires exactly 2 products"
        
        product1, product2 = products
        
        battle_text = []
        battle_text.append("⚔️  PRODUCT BATTLE")
        battle_text.append(f"\n{product1['name']} VS {product2['name']}\n")
        
        rounds = []
        
        # Round 1: Price
        rounds.append({
            "name": "ROUND 1: PRICE 💰",
            "p1_value": f"₹{product1['price']:,.0f}",
            "p2_value": f"₹{product2['price']:,.0f}",
            "winner": product1['name'] if product1['price'] < product2['price'] else product2['name'],
            "reason": f"₹{abs(product1['price'] - product2['price']):,.0f} cheaper"
        })
        
        # Round 2: Rating
        rounds.append({
            "name": "ROUND 2: RATING ⭐",
            "p1_value": f"{product1['rating']}/5 ({product1['review_count']} reviews)",
            "p2_value": f"{product2['rating']}/5 ({product2['review_count']} reviews)",
            "winner": product1['name'] if product1['rating'] > product2['rating'] else product2['name'],
            "reason": f"{abs(product1['rating'] - product2['rating']):.1f} stars better"
        })
        
        # Round 3: Discount
        rounds.append({
            "name": "ROUND 3: DISCOUNT 🎁",
            "p1_value": f"{product1['discount_pct']}% OFF",
            "p2_value": f"{product2['discount_pct']}% OFF",
            "winner": product1['name'] if product1['discount_pct'] > product2['discount_pct'] else product2['name'],
            "reason": f"{abs(product1['discount_pct'] - product2['discount_pct']):.1f}% more savings"
        })
        
        # Format rounds
        for round_data in rounds:
            battle_text.append("┌" + "─" * 60 + "┐")
            battle_text.append(f"│  {round_data['name']:<56}  │")
            battle_text.append("├" + "─" * 60 + "┤")
            battle_text.append(f"│  {product1['name'][:25]:<25}: {round_data['p1_value']:<30}│")
            battle_text.append(f"│  {product2['name'][:25]:<25}: {round_data['p2_value']:<30}│")
            battle_text.append("│" + " " * 60 + "│")
            battle_text.append(f"│  🏆 WINNER: {round_data['winner']:<45}│")
            battle_text.append(f"│  Reason: {round_data['reason']:<49}│")
            battle_text.append("└" + "─" * 60 + "┘")
            battle_text.append("")
        
        # Calculate overall winner
        p1_wins = sum(1 for r in rounds if r['winner'] == product1['name'])
        p2_wins = sum(1 for r in rounds if r['winner'] == product2['name'])
        
        battle_text.append("🏆 FINAL VERDICT:")
        if p1_wins > p2_wins:
            battle_text.append(f"   Winner: {product1['name']} ({p1_wins} rounds)")
        elif p2_wins > p1_wins:
            battle_text.append(f"   Winner: {product2['name']} ({p2_wins} rounds)")
        else:
            battle_text.append("   It's a TIE! Both products are equally matched")
        
        return "\n".join(battle_text)


# Global instance
comparison_tools = ComparisonTools()
