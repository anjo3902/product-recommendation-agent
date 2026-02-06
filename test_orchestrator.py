import sys
import asyncio
sys.path.insert(0, 'C:\\Users\\ANJO JAISON\\Downloads\\Product Recommendation Agent')

print("\n🧪 Testing Orchestrator Agent...\n")

async def test():
    try:
        from src.agents.orchestrator_agent import orchestrator_agent
        
        print("Calling orchestrator with query: 'laptop'")
        result = await orchestrator_agent.orchestrate_recommendation(
            query="laptop",
            top_n=3
        )
        
        print(f"\nSuccess: {result.get('success')}")
        
        if result.get('success'):
            print(f"Products: {len(result.get('products', []))}")
            for p in result.get('products', [])[:2]:
                print(f"  - {p['name']}")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
