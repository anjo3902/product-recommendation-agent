import sys
import asyncio
sys.path.insert(0, '.')

from src.agents.orchestrator_agent import OrchestratorAgent

async def test():
    # Create orchestrator
    print("Creating OrchestratorAgent...")
    orchestrator = OrchestratorAgent()
    
    # Test 1: Single word (works)
    print("\n" + "="*60)
    print("TEST 1: 'laptops'")
    print("="*60)
    try:
        result1 = await orchestrator.orchestrate_recommendation("laptops", limit=3)
        print(f"Success: {result1.get('success')}")
        print(f"Products: {len(result1.get('products', []))}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Multi-word (fails)
    print("\n" + "="*60)
    print("TEST 2: 'gaming laptop'")
    print("="*60)
    try:
        result2 = await orchestrator.orchestrate_recommendation("gaming laptop", limit=3)
        print(f"Success: {result2.get('success')}")
        print(f"Products: {len(result2.get('products', []))}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

# Run async test
asyncio.run(test())
