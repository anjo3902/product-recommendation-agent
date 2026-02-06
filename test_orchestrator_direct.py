import asyncio
import sys
sys.path.insert(0, '.')
from src.agents.orchestrator_agent import OrchestratorAgent

async def test():
    agent = OrchestratorAgent()
    
    # Test both queries
    for query in ['laptop', 'gaming laptop', 'best laptops for gaming']:
        print(f'\n=== Testing: {query} ===')
        result = await agent.orchestrate_recommendation(query)
        print(f'Success: {result.get("success")}')
        print(f'Products: {len(result.get("products", []))}')
        if not result.get('success'):
            print(f'Error: {result.get("error")}')
            print(f'Full result: {result}')
        else:
            print(f'Product 1: {result["products"][0]["name"]}')
        print()

asyncio.run(test())
