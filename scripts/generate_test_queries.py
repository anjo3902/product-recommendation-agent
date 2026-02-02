"""
Generate test queries for evaluation
"""

import json
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

TEST_QUERIES = {
    # Search queries
    'search_queries': [
        {
            'query': 'wireless headphones under 3000',
            'category': 'Electronics',
            'budget': 3000,
            'expected_features': ['Wireless', 'Bluetooth']
        },
        {
            'query': 'gaming laptop with good graphics',
            'category': 'Electronics',
            'budget': 80000,
            'expected_features': ['Dedicated Graphics', 'Gaming']
        },
        {
            'query': 'smartphone with good camera under 20000',
            'category': 'Electronics',
            'budget': 20000,
            'expected_features': ['Multiple Cameras', 'Photography']
        },
        {
            'query': 'running shoes for men',
            'category': 'Fashion',
            'budget': 5000,
            'expected_features': ['Comfortable', 'Cushioned']
        },
        {
            'query': 'best headphones for gym',
            'category': 'Electronics',
            'budget': 5000,
            'expected_features': ['Water Resistant', 'Wireless']
        },
        {
            'query': 'laptop for programming under 60000',
            'category': 'Electronics',
            'budget': 60000,
            'expected_features': ['16GB RAM', 'SSD Storage']
        },
        {
            'query': 'kitchen appliances for daily cooking',
            'category': 'Home & Kitchen',
            'budget': 10000,
            'expected_features': ['Energy Efficient', 'Durable']
        },
        {
            'query': 'fitness equipment for home workout',
            'category': 'Sports',
            'budget': 5000,
            'expected_features': ['Compact', 'Durable']
        }
    ],
    
    # Comparison queries
    'comparison_queries': [
        {
            'product_ids': [1, 2, 3],
            'comparison_type': 'feature',
            'focus': 'battery life'
        },
        {
            'product_ids': [10, 11, 12],
            'comparison_type': 'price_performance',
            'focus': 'value for money'
        },
        {
            'product_ids': [5, 6, 7],
            'comparison_type': 'specifications',
            'focus': 'technical specs'
        }
    ],
    
    # Review analysis queries
    'review_queries': [
        {
            'product_id': 1,
            'question': 'Is battery life good?'
        },
        {
            'product_id': 2,
            'question': 'How is the build quality?'
        },
        {
            'product_id': 3,
            'question': 'Is it good for gaming?'
        },
        {
            'product_id': 5,
            'question': 'Does it have noise cancellation?'
        }
    ],
    
    # Budget optimization queries
    'budget_queries': [
        {
            'items': [
                {'category': 'Headphones', 'budget': 3000},
                {'category': 'Smartphones', 'budget': 20000}
            ],
            'total_budget': 25000
        },
        {
            'items': [
                {'category': 'Laptop', 'budget': 50000},
                {'category': 'Headphones', 'budget': 5000}
            ],
            'total_budget': 60000
        }
    ]
}

# Save to JSON
with open('data/test_queries.json', 'w') as f:
    json.dump(TEST_QUERIES, f, indent=2)

print("✅ Test queries generated successfully!")
print(f"📁 File: data/test_queries.json")
print(f"📊 Search queries: {len(TEST_QUERIES['search_queries'])}")
print(f"🔄 Comparison queries: {len(TEST_QUERIES['comparison_queries'])}")
print(f"💬 Review queries: {len(TEST_QUERIES['review_queries'])}")
print(f"💰 Budget queries: {len(TEST_QUERIES['budget_queries'])}")
