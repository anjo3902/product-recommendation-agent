import sys
sys.path.insert(0, 'C:\\Users\\ANJO JAISON\\Downloads\\Product Recommendation Agent')

print("\n🧪 Testing Product Search...\n")

try:
    from src.agents.product_search_agent import ProductSearchAgent
    
    agent = ProductSearchAgent()
    result = agent.search_products('laptop', limit=3)
    
    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count', 0)}")
    
    if result.get('products'):
        print(f"\n✅ Found products:")
        for p in result['products'][:3]:
            print(f"  - {p['name']} (₹{p['price']})")
    else:
        print(f"\n❌ No products found")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
