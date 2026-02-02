"""
ChromaDB Setup - Vector Database for Semantic Search
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
import os


def setup_chroma_db():
    """Initialize ChromaDB for semantic search"""
    
    # Create data directory
    chroma_path = "./data/chroma_db"
    os.makedirs(chroma_path, exist_ok=True)
    
    # Initialize client
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    # Create products collection
    try:
        collection = client.create_collection(
            name="products",
            metadata={
                "hnsw:space": "cosine",  # Use cosine similarity
                "description": "Product embeddings for semantic search"
            }
        )
        print("✅ ChromaDB collection 'products' created successfully!")
    except Exception as e:
        print(f"ℹ️  Collection might already exist: {e}")
        collection = client.get_collection(name="products")
        print("✅ Using existing 'products' collection")
    
    return client, collection


def get_chroma_client():
    """Get ChromaDB client (reusable)"""
    chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=ChromaSettings(
            anonymized_telemetry=False
        )
    )
    
    return client


def get_products_collection():
    """Get products collection from ChromaDB"""
    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name="products")
    except Exception:
        # Create if doesn't exist
        collection = client.create_collection(
            name="products",
            metadata={
                "hnsw:space": "cosine",
                "description": "Product embeddings for semantic search"
            }
        )
    
    return collection


if __name__ == "__main__":
    client, collection = setup_chroma_db()
    print(f"✅ ChromaDB setup complete!")
    print(f"📁 Database location: {os.path.abspath('./data/chroma_db')}")
    print(f"📊 Collection count: {collection.count()}")
