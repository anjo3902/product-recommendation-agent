from src.database.session import SessionLocal
from src.database.models import Product

db = SessionLocal()
count = db.query(Product).count()
print(f'\n📦 Total products in database: {count}')

if count > 0:
    sample = db.query(Product).limit(5).all()
    print('\n✅ Sample products:')
    for p in sample:
        print(f'  - {p.name} (₹{p.price})')
else:
    print('\n❌ NO PRODUCTS IN DATABASE!')
    print('   Run: python scripts/generate_sample_data.py')

db.close()
