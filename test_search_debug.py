import sys
sys.path.insert(0, '.')

from src.agents.product_search_agent import ProductSearchAgent

# Create agent
print("Creating ProductSearchAgent...")
agent = ProductSearchAgent()

# Test 1: Single word (works)
print("\n" + "="*60)
print("TEST 1: 'laptops'")
print("="*60)
result1 = agent.search_products("laptops", limit=3)
print(f"Success: {result1.get('success')}")
print(f"Products found: {result1.get('count', 0)}")
if not result1.get('success'):
    print(f"ERROR: {result1.get('error')}")
else:
    print(f"Intent parsed: {result1.get('intent')}")

# Test 2: Multi-word (fails)
print("\n" + "="*60)
print("TEST 2: 'gaming laptop'")
print("="*60)
try:
    result2 = agent.search_products("gaming laptop", limit=3)
    print(f"Success: {result2.get('success')}")
    print(f"Products found: {result2.get('count', 0)}")
    if not result2.get('success'):
        print(f"ERROR: {result2.get('error')}")
    else:
        print(f"Intent parsed: {result2.get('intent')}")
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
