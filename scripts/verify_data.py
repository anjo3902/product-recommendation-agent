"""
Verify generated data quality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import Product, Review, PriceHistory

def verify_data():
    db = SessionLocal()
    
    try:
        print("\n🔍 DATA QUALITY VERIFICATION")
        print("=" * 70)
        
        # Check products
        total_products = db.query(Product).count()
        print(f"\n✅ Total Products: {total_products}")
        
        if total_products == 0:
            print("\n⚠️  No products found in database!")
            print("👉 Run: python scripts/generate_sample_data.py")
            return
        
        products_with_reviews = db.query(Product).filter(Product.review_count > 0).count()
        print(f"✅ Products with Reviews: {products_with_reviews} ({products_with_reviews/total_products*100:.1f}%)")
        
        in_stock = db.query(Product).filter(Product.in_stock == True).count()
        print(f"✅ Products In Stock: {in_stock} ({in_stock/total_products*100:.1f}%)")
        
        # Check reviews
        total_reviews = db.query(Review).count()
        print(f"\n⭐ Total Reviews: {total_reviews}")
        
        if total_reviews > 0:
            verified_reviews = db.query(Review).filter(Review.verified_purchase == True).count()
            print(f"✅ Verified Reviews: {verified_reviews} ({verified_reviews/total_reviews*100:.1f}%)")
            
            # Rating distribution
            print("\n📊 Rating Distribution:")
            for rating in [5, 4, 3, 2, 1]:
                count = db.query(Review).filter(Review.rating == rating).count()
                bar = '█' * int(count / total_reviews * 50)
                print(f"  {rating}⭐: {count:4d} {bar}")
        
        # Check price history
        total_price_records = db.query(PriceHistory).count()
        print(f"\n💰 Total Price History Records: {total_price_records}")
        if total_products > 0:
            print(f"📈 Average records per product: {total_price_records/total_products:.1f}")
        
        # Sample products
        print("\n📦 SAMPLE PRODUCTS:")
        print("-" * 70)
        
        for product in db.query(Product).limit(5):
            print(f"\n{product.name}")
            print(f"  Price: ₹{product.price}")
            print(f"  Rating: {product.rating}⭐ ({product.review_count} reviews)")
            print(f"  Category: {product.category} > {product.subcategory}")
            print(f"  In Stock: {'Yes' if product.in_stock else 'No'}")
        
        print("\n" + "=" * 70)
        print("✅ DATA QUALITY VERIFICATION COMPLETE!")
        
        if total_products >= 50 and total_reviews >= 200:
            print("🎉 Data is ready for production testing!")
        else:
            print("⚠️  Consider generating more data for comprehensive testing")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()
