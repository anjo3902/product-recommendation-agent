"""
Product Embeddings Generator - Creates vector representations for semantic search
"""
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from src.database.models import Product
from src.database.connection import get_db
from src.database.setup_vector_db import get_products_collection


class EmbeddingGenerator:
    """Generate and manage product embeddings"""
    
    def __init__(self):
        """Initialize the embedding model"""
        # Use fastembed - lightweight, no PyTorch DLL issues
        from fastembed import TextEmbedding
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        print("[OK] Embedding model loaded: BAAI/bge-small-en-v1.5 (fastembed)")
    
    def create_product_text(self, product: Product) -> str:
        """
        Create searchable text from product data
        
        Combines: name, brand, category, features, specs
        """
        # Parse features and specs
        try:
            features = json.loads(product.features) if product.features else []
        except:
            features = []
        
        try:
            specs = json.loads(product.specifications) if product.specifications else {}
        except:
            specs = {}
        
        # Build comprehensive text
        text_parts = [
            product.name,
            product.brand,
            product.category,
            product.subcategory or "",
            product.model or "",
            product.description or "",
            " ".join(features),
            " ".join([f"{k}: {v}" for k, v in specs.items()])
        ]
        
        # Clean and join
        text = " ".join([part for part in text_parts if part]).strip()
        return text
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        # fastembed returns generator, get first result
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()
    
    def populate_vector_db(self, batch_size: int = 100):
        """
        Load all products from PostgreSQL and create embeddings in ChromaDB
        
        Args:
            batch_size: Number of products to process at once
        """
        db = next(get_db())
        collection = get_products_collection()
        
        try:
            # Get total count
            total_products = db.query(Product).count()
            print(f"📊 Found {total_products} products in database")
            
            # Clear existing embeddings
            try:
                collection.delete(where={})
                print("🗑️  Cleared existing embeddings")
            except:
                pass
            
            # Process in batches
            processed = 0
            
            for offset in range(0, total_products, batch_size):
                products = db.query(Product).offset(offset).limit(batch_size).all()
                
                # Prepare batch data
                ids = []
                documents = []
                metadatas = []
                embeddings = []
                
                for product in products:
                    # Create searchable text
                    text = self.create_product_text(product)
                    
                    # Generate embedding
                    embedding = self.generate_embedding(text)
                    
                    # Parse features for metadata
                    try:
                        features = json.loads(product.features) if product.features else []
                    except:
                        features = []
                    
                    # Add to batch
                    ids.append(str(product.id))
                    documents.append(text)
                    embeddings.append(embedding)
                    metadatas.append({
                        "product_id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "category": product.category,
                        "subcategory": product.subcategory or "",
                        "price": float(product.price),
                        "rating": float(product.rating),
                        "review_count": product.review_count,
                        "features": json.dumps(features)  # Store as JSON string
                    })
                
                # Add batch to ChromaDB
                collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                
                processed += len(products)
                print(f"✅ Processed {processed}/{total_products} products ({(processed/total_products)*100:.1f}%)")
            
            print(f"\n🎉 Successfully created embeddings for {processed} products!")
            print(f"📊 Vector DB count: {collection.count()}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
        finally:
            db.close()
    
    def search_similar_products(
        self, 
        query: str, 
        n_results: int = 10,
        category_filter: str = None,
        min_price: float = None,
        max_price: float = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for products using natural language
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            category_filter: Optional category OR subcategory filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            
        Returns:
            List of products with similarity scores
        """
        collection = get_products_collection()
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Build where filter - FIXED: Check both category AND subcategory
        where_filter = None
        if category_filter:
            # Don't use exact match - we'll filter after search
            # This allows matching both category and subcategory
            pass
        
        # Search without category filter (we'll filter after by subcategory)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 3,  # Get more to filter
            include=["metadatas", "distances", "documents"]
        )
        
        # Parse results
        products = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            # Category/Subcategory filtering (case-insensitive)
            if category_filter:
                category = metadata.get('category', '').lower()
                subcategory = metadata.get('subcategory', '').lower()
                filter_lower = category_filter.lower()
                
                # Match if filter matches either category or subcategory
                if filter_lower not in category and filter_lower not in subcategory:
                    continue
            
            # Price filtering
            price = metadata.get('price', 0)
            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue
            
            # Calculate similarity score (1 - distance for cosine)
            similarity = 1 - distance
            
            products.append({
                "product_id": metadata['product_id'],
                "name": metadata['name'],
                "brand": metadata['brand'],
                "category": metadata['category'],
                "subcategory": metadata['subcategory'],
                "price": metadata['price'],
                "rating": metadata['rating'],
                "review_count": metadata['review_count'],
                "features": json.loads(metadata['features']),
                "similarity_score": round(similarity, 4),
                "match_text": results['documents'][0][i][:200] + "..."
            })
            
            if len(products) >= n_results:
                break
        
        return products


def populate_embeddings():
    """Helper function to populate embeddings from command line"""
    print("🚀 Starting embedding generation...")
    generator = EmbeddingGenerator()
    generator.populate_vector_db()
    print("✅ Done!")


if __name__ == "__main__":
    populate_embeddings()
