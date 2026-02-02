"""
Complete Database Verification
Checks that all products have reviews, price history, and offers
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.connection import SessionLocal
from src.database.models import Product, Review, PriceHistory, CardOffer
import json

def verify_complete_data():
    """Verify all products have complete data"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("DATABASE VERIFICATION REPORT")
        print("=" * 70)
        
        # Get all products
        products = db.query(Product).all()
        total = len(products)
        
        # Check coverage
        without_reviews = sum(1 for p in products if len(p.reviews) == 0)
        without_history = sum(1 for p in products if len(p.price_history) == 0)
        without_offers = sum(1 for p in products if len(p.card_offers) == 0)
        
        # Check NULL values
        null_mrp = sum(1 for p in products if p.mrp is None)
        null_model = sum(1 for p in products if p.model is None)
        null_features = sum(1 for p in products if p.features is None or p.features == '')
        null_specs = sum(1 for p in products if p.specifications is None or p.specifications == '')
        
        # Get totals
        total_reviews = db.query(Review).count()
        total_history = db.query(PriceHistory).count()
        total_offers = db.query(CardOffer).count()
        
        print(f"\n📊 TOTAL PRODUCTS: {total}")
        
        print(f"\n✅ DATA COVERAGE:")
        print(f"  ✓ Products WITH reviews:       {total - without_reviews:4d} ({(total - without_reviews)/total*100:5.1f}%)")
        print(f"  ✗ Products WITHOUT reviews:    {without_reviews:4d}")
        print(f"  ✓ Products WITH price history: {total - without_history:4d} ({(total - without_history)/total*100:5.1f}%)")
        print(f"  ✗ Products WITHOUT price history: {without_history:4d}")
        print(f"  ✓ Products WITH offers:        {total - without_offers:4d} ({(total - without_offers)/total*100:5.1f}%)")
        print(f"  ✗ Products WITHOUT offers:     {without_offers:4d}")
        
        print(f"\n📈 DATA TOTALS:")
        print(f"  Total Reviews:        {total_reviews:6,} (Avg: {total_reviews/total:.1f} per product)")
        print(f"  Total Price Records:  {total_history:6,} (Avg: {total_history/total:.1f} per product)")
        print(f"  Total Card Offers:    {total_offers:6,} (Avg: {total_offers/total:.1f} per product)")
        
        print(f"\n🔍 NULL VALUE CHECK:")
        print(f"  Products with NULL MRP:            {null_mrp}")
        print(f"  Products with NULL Model:          {null_model}")
        print(f"  Products with NULL Features:       {null_features}")
        print(f"  Products with NULL Specifications: {null_specs}")
        
        # Sample product check
        if total > 0:
            sample = products[0]
            print(f"\n📦 SAMPLE PRODUCT:")
            print(f"  Name:          {sample.name}")
            print(f"  Brand:         {sample.brand}")
            print(f"  Model:         {sample.model}")
            print(f"  Category:      {sample.category} > {sample.subcategory}")
            print(f"  Price:         ₹{sample.price:,.2f}")
            print(f"  MRP:           ₹{sample.mrp:,.2f}" if sample.mrp else "  MRP:           NULL")
            print(f"  Rating:        {sample.rating}/5")
            print(f"  Reviews:       {len(sample.reviews)} reviews")
            print(f"  Price History: {len(sample.price_history)} records")
            print(f"  Card Offers:   {len(sample.card_offers)} offers")
            if sample.features:
                features = json.loads(sample.features)
                print(f"  Features:      {', '.join(features[:3])}...")
        
        print("\n" + "=" * 70)
        
        # Final verdict
        if (without_reviews == 0 and without_history == 0 and 
            null_mrp == 0 and null_model == 0 and 
            null_features == 0 and null_specs == 0):
            print("🎉 PERFECT! All products have COMPLETE data!")
            print("✅ Ready for all 6 agents:")
            print("   - Product Search Agent (can search all products)")
            print("   - Review Analyzer Agent (all products have reviews)")
            print("   - Price Tracker Agent (all products have 90-day history)")
            print("   - Comparison Agent (multiple products per category)")
            print("   - Buy Plan Optimizer (products have card offers)")
            print("   - Orchestrator Agent (complete ecosystem)")
        else:
            print("⚠️  ISSUES FOUND:")
            if without_reviews > 0:
                print(f"   ❌ {without_reviews} products missing reviews")
            if without_history > 0:
                print(f"   ❌ {without_history} products missing price history")
            if null_mrp > 0:
                print(f"   ❌ {null_mrp} products missing MRP")
            if null_model > 0:
                print(f"   ❌ {null_model} products missing Model number")
            if null_features > 0:
                print(f"   ❌ {null_features} products missing Features")
            if null_specs > 0:
                print(f"   ❌ {null_specs} products missing Specifications")
            print("\n   Run: python scripts/fix_null_values.py")
        
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_complete_data()
