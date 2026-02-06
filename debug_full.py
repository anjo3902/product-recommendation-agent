import sys
import asyncio
sys.path.insert(0, 'C:\\Users\\ANJO JAISON\\Downloads\\Product Recommendation Agent')

print("\n🔍 DEBUGGING: Testing gaming laptop query...\n")

async def test():
    try:
        print("[1] Testing Product Search Agent...")
        from src.agents.product_search_agent import ProductSearchAgent
        
        agent = ProductSearchAgent()
        search_result = agent.search_products(
            query='gaming laptop',
            max_price=80000,
            limit=5
        )
        
        print(f"  Success: {search_result.get('success')}")
        print(f"  Products: {len(search_result.get('products', []))}")
        
        if search_result.get('products'):
            print(f"\n  Sample products:")
            for p in search_result['products'][:3]:
                print(f"    - {p['name']} (₹{p['price']})")
        else:
            print(f"  Error: {search_result.get('error', 'No products')}")
        
        print("\n[2] Testing Orchestrator Agent...")
        from src.agents.orchestrator_agent import orchestrator_agent
        
        result = await orchestrator_agent.orchestrate_recommendation(
            query="Find gaming laptops under 80000",
            top_n=3
        )
        
        print(f"  Success: {result.get('success')}")
        print(f"  Products: {len(result.get('products', []))}")
        print(f"  Error: {result.get('error', 'None')}")
        
        if result.get('products'):
            print(f"\n  ✅ ORCHESTRATOR WORKS!")
            for p in result['products'][:2]:
                print(f"    - {p['name']}")
        else:
            print(f"\n  ❌ ORCHESTRATOR FAILED: {result.get('error')}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
