"""
Populate ChromaDB Vector Database with Product Embeddings
Run after generating/updating product data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.embeddings import populate_embeddings

if __name__ == "__main__":
    print("=" * 70)
    print(" CHROMADB VECTOR DATABASE POPULATION")
    print("=" * 70)
    populate_embeddings()
    print("=" * 70)
    print("✅ Vector database updated successfully!")
    print("💡 Backend will now be able to search products using AI semantic search")
    print("=" * 70)
