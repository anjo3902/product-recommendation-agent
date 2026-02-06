"""
Clear ChromaDB and rebuild from scratch
"""
import sys
import os
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Delete the entire ChromaDB directory
chroma_path =  "./data/chroma_db"
if os.path.exists(chroma_path):
    print(f"🗑️  Deleting ChromaDB directory: {chroma_path}")
    shutil.rmtree(chroma_path)
    print("✅ ChromaDB directory deleted!")
else:
    print(f"ℹ️  ChromaDB directory not found: {chroma_path}")

print("\n🔄 Rebuilding vector database...")

from src.database.embeddings import populate_embeddings
populate_embeddings()

print("\n✅ ChromaDB rebuilt successfully!")
