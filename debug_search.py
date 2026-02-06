import sys
sys.path.insert(0, 'C:\\Users\\ANJO JAISON\\Downloads\\Product Recommendation Agent')

from src.database.session import SessionLocal
from src.database.models import Product

db = SessionLocal()

# Get total count
total = db.query(Product).count()
print(f"\n📦 Total products: {total}")

if total > 0:
    # Get a few samples
    products = db.query(Product).limit(10).all()
    print("\n✅ Sample products:")
    for p in products:
        print(f"  ID: {p.id}")
        print(f"  Name: {p.name}")
        print(f"  Category: {p.category}")
        print(f"  Subcategory: {p.subcategory}")
        print(f"  Brand: {p.brand}")
        print(f"  Price: ₹{p.price}")
        print(f"  ---")
    
    # Check for laptops specifically
    print("\n🔍 Searching for laptops...")
    laptops = db.query(Product).filter(
        Product.name.ilike('%laptop%')
    ).limit(5).all()
    print(f"Found {len(laptops)} laptops by name")
    
    laptops_cat = db.query(Product).filter(
        Product.category.ilike('%laptop%')
    ).limit(5).all()
    print(f"Found {len(laptops_cat)} products in laptop category")
    
else:
    print("\n❌ No products in database!")
    print("   Run: python scripts/generate_sample_data.py")

db.close()
