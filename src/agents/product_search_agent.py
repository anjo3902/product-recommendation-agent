"""
Product Search Agent - Intelligent product search using Ollama (Local LLM) + Hybrid Search
"""
import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
import ollama

from src.database.models import Product, Review, PriceHistory, CardOffer
from src.database.connection import get_db
from src.database.embeddings import EmbeddingGenerator


class ProductSearchAgent:
    """AI-powered product search agent using Ollama (Local LLM) + ChromaDB"""
    
    def __init__(self):
        """Initialize the agent with Ollama and embedding model"""
        # Initialize Ollama client (runs locally, no API key needed)
        self.client = ollama
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.1')  # Default: Llama 3.1
        
        # Test Ollama connection
        try:
            self.client.list()  # Check if Ollama is running
            print(f"[OK] Ollama connected! Using model: {self.model_name}")
        except Exception as e:
            print(f"[WARN] Ollama not running. Start with: ollama serve")
            print(f"   Error: {e}")
        
        # Initialize embedding generator for semantic search
        self.embedder = EmbeddingGenerator()
    
    def search_products(
        self, 
        query: str, 
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        🔍 HYBRID SEARCH: Semantic (ChromaDB) + Traditional (PostgreSQL)
        
        Args:
            query: Natural language search query
            category: Optional category filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum rating filter
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results and AI insights
        """
        import sys
        sys.stdout.write(f"[SEARCH] Starting search for: '{query}'\n")
        sys.stdout.flush()
        
        db = next(get_db())
        
        try:
            # Step 1: Parse query intent using Gemini
            sys.stdout.write(f"[SEARCH] Parsing intent...\n")
            sys.stdout.flush()
            intent = self._parse_search_intent(query)
            sys.stdout.write(f"[SEARCH] Intent parsed: {intent}\n")
            sys.stdout.flush()
            
            # Extract category from intent if not provided
            if not category and intent.get('category'):
                category = intent['category']
            
            # Extract price range from intent - handle various formats from LLM
            if intent.get('price_range'):
                try:
                    price_range = intent['price_range']
                    # Handle list/tuple format: [min, max]
                    if isinstance(price_range, (list, tuple)) and len(price_range) == 2:
                        price_min, price_max = price_range
                        if not min_price and price_min:
                            min_price = price_min
                        if not max_price and price_max:
                            max_price = price_max
                    # Handle single value (treat as max price)
                    elif isinstance(price_range, (int, float)):
                        if not max_price:
                            max_price = price_range
                except (ValueError, TypeError) as e:
                    # Log and continue if price parsing fails
                    print(f"Price range parsing warning: {e}")
            
            # Step 2: SEMANTIC SEARCH using ChromaDB (70% weight)
            sys.stdout.write(f"[SEARCH] Running semantic search...\n")
            sys.stdout.flush()
            semantic_results = self.embedder.search_similar_products(
                query=query,
                n_results=limit * 2,  # Get more for better ranking
                category_filter=category,
                min_price=min_price,
                max_price=max_price
            )
            sys.stdout.write(f"[SEARCH] Semantic results: {len(semantic_results)} products\n")
            sys.stdout.flush()
            
            # Step 3: TRADITIONAL SEARCH using PostgreSQL (30% weight)
            sys.stdout.write(f"[SEARCH] Running traditional search...\n")
            sys.stdout.flush()
            traditional_results = self._traditional_search(
                db=db,
                intent=intent,
                category=category,
                min_price=min_price,
                max_price=max_price,
                min_rating=min_rating,
                limit=limit * 2
            )
            sys.stdout.write(f"[SEARCH] Traditional results: {len(traditional_results)} products\n")
            sys.stdout.flush()
            
            # Step 4: HYBRID RANKING - Combine both results
            sys.stdout.write(f"[SEARCH] Combining results...\n")
            sys.stdout.flush()
            combined_products = self._combine_and_rank(
                semantic_results=semantic_results,
                traditional_results=traditional_results,
                limit=limit
            )
            sys.stdout.write(f"[SEARCH] Combined results: {len(combined_products)} products\n")
            sys.stdout.flush()
            
            # Step 5: Enrich results with AI insights
            results = self._enrich_results(combined_products, query, intent)
            
            return {
                "success": True,
                "query": query,
                "products": results['products'],
                "count": len(combined_products),              # Guide standard
                "reasoning": results['summary'],              # Guide standard
                "recommendations": results['recommendations'],
                # Extra fields for detailed insights
                "intent": intent,
                "search_method": "hybrid",
                "semantic_count": len(semantic_results),
                "traditional_count": len(traditional_results),
                "total_results": len(combined_products),      # Backwards compatibility
                "ai_summary": results['summary']              # Backwards compatibility
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
        finally:
            db.close()
    
    def _traditional_search(
        self,
        db: Session,
        intent: Dict[str, Any],
        category: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        min_rating: Optional[float],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Traditional keyword-based PostgreSQL search"""
        products_query = db.query(Product)
        filters = []
        
        # Category filter - check BOTH category AND subcategory fields
        if category:
            filters.append(
                or_(
                    Product.category.ilike(f"%{category}%"),
                    Product.subcategory.ilike(f"%{category}%")
                )
            )
        
        # Brand filter
        if intent.get('brand'):
            filters.append(Product.brand.ilike(f"%{intent['brand']}%"))
        
        # Price filters
        if min_price:
            filters.append(Product.price >= min_price)
        if max_price:
            filters.append(Product.price <= max_price)
        
        # Rating filter
        if min_rating:
            filters.append(Product.rating >= min_rating)
        
        # Keyword search (expanded to more fields) - OR logic for better recall
        if intent.get('keywords'):
            keyword_filters = []
            for keyword in intent['keywords']:
                # Search in name, description, category, subcategory, brand, model
                keyword_filters.append(Product.name.ilike(f"%{keyword}%"))
                keyword_filters.append(Product.description.ilike(f"%{keyword}%"))
                keyword_filters.append(Product.category.ilike(f"%{keyword}%"))
                keyword_filters.append(Product.subcategory.ilike(f"%{keyword}%"))
                keyword_filters.append(Product.brand.ilike(f"%{keyword}%"))
                keyword_filters.append(Product.model.ilike(f"%{keyword}%"))
                keyword_filters.append(Product.features.ilike(f"%{keyword}%"))
            # Use OR - match if ANY keyword is found in ANY field
            if keyword_filters:
                filters.append(or_(*keyword_filters))
        
        # Apply filters
        if filters:
            products_query = products_query.filter(and_(*filters))
        
        # Sort by popularity
        products_query = products_query.order_by(
            (Product.rating * Product.review_count).desc()
        ).limit(limit)
        
        products = products_query.all()
        
        # Convert to dictionaries
        results = []
        for product in products:
            try:
                features = json.loads(product.features) if product.features else []
            except:
                features = []
            
            results.append({
                "product_id": product.id,
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "price": float(product.price),
                "rating": float(product.rating),
                "review_count": product.review_count,
                "features": features,
                "search_score": 0.3  # Traditional search weight
            })
        
        return results
    
    def _combine_and_rank(
        self,
        semantic_results: List[Dict[str, Any]],
        traditional_results: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Hybrid ranking: 70% semantic similarity + 30% keyword match
        """
        # Create combined dictionary by product_id
        combined = {}
        
        # Add semantic results (70% weight)
        for result in semantic_results:
            product_id = result['product_id']
            combined[product_id] = result.copy()
            combined[product_id]['final_score'] = result.get('similarity_score', 0.5) * 0.7
        
        # Add/merge traditional results (30% weight)
        for result in traditional_results:
            product_id = result['product_id']
            if product_id in combined:
                # Boost score for products found in both
                combined[product_id]['final_score'] += 0.3
            else:
                combined[product_id] = result.copy()
                combined[product_id]['final_score'] = 0.3
        
        # Sort by final score
        ranked_products = sorted(
            combined.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )[:limit]
        
        return ranked_products
    
    def _parse_search_intent(self, query: str) -> Dict[str, Any]:
        """
        Use Ollama to understand search intent (with fallback)
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with parsed intent (category, brand, keywords, price_range, etc.)
        """
        # Fallback intent (will be used if LLM fails)
        fallback_intent = {
            "keywords": query.lower().split(),
            "intent": query
        }
        
        prompt = f"""Analyze this product search query and extract structured information.

Query: "{query}"

Extract the following information in JSON format:
{{
    "category": "product category (Smartphones, Laptops, or Headphones)",
    "brand": "brand name if mentioned",
    "keywords": ["list", "of", "important", "keywords"],
    "price_range": [min_price_number_only, max_price_number_only] or null,
    "features": ["specific", "features", "mentioned"],
    "intent": "brief description of what user wants"
}}

Examples:
- "best gaming laptop under 80000" → {{"category": "Laptops", "keywords": ["gaming"], "price_range": [null, 80000]}}
- "Samsung phone with good camera" → {{"category": "Smartphones", "brand": "Samsung", "keywords": ["camera"]}}
- "wireless headphones" → {{"category": "Headphones", "keywords": ["wireless"]}}

Return ONLY valid JSON, no other text."""

        try:
            # Call Ollama API
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                format='json',  # Force JSON output
                options={
                    'temperature': 0.1,  # Low temperature for consistency
                    'num_predict': 200   # Limit tokens
                }
            )
            
            # Extract JSON from response
            response_text = response['response'].strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            intent = json.loads(response_text)
            return intent
            
        except Exception as e:
            # Log error for debugging
            print(f"Ollama Intent Parsing (using fallback): {e}")
            # Return fallback
            return fallback_intent
    
    def _enrich_results(
        self, 
        products: List[Dict[str, Any]], 
        query: str, 
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich product results with full details from database and AI insights
        
        Args:
            products: List of product dictionaries (from hybrid search)
            query: Original search query
            intent: Parsed intent
            
        Returns:
            Dictionary with enriched product data and AI summary
        """
        # Get full product details from database
        db = next(get_db())
        product_ids = [p['product_id'] for p in products]
        
        full_products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        db.close()
        
        # Create lookup dict
        product_dict = {p.id: p for p in full_products}
        
        # Enrich with full details
        enriched_list = []
        for search_result in products:
            product_id = search_result['product_id']
            product = product_dict.get(product_id)
            
            if not product:
                continue
            
            # Parse features and specs
            try:
                features = json.loads(product.features) if product.features else []
            except:
                features = []
            
            try:
                specs = json.loads(product.specifications) if product.specifications else {}
            except:
                specs = {}
            
            # Format specifications for better readability
            formatted_specs = self._format_specifications(specs)
            
            enriched_list.append({
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "model": product.model,
                "category": product.category,
                "subcategory": product.subcategory,
                "price": float(product.price),
                "mrp": float(product.mrp) if product.mrp else float(product.price),
                "discount_percent": round(((float(product.mrp or product.price) - float(product.price)) / float(product.mrp or product.price)) * 100, 1) if product.mrp else 0,
                "rating": float(product.rating),
                "review_count": product.review_count,
                "in_stock": product.in_stock,
                "description": product.description[:200] + "..." if product.description and len(product.description) > 200 else product.description,
                "features": features,
                "specifications": specs,
                "key_specs": formatted_specs,  # Highlighted key specifications
                "search_score": search_result.get('final_score', search_result.get('similarity_score', 0))
            })
        
        # Generate AI summary
        if enriched_list:
            summary = self._generate_summary(enriched_list, query, intent)
            recommendations = self._generate_recommendations(enriched_list, query)
        else:
            summary = f"No products found matching '{query}'. Try different keywords or broader search terms."
            recommendations = []
        
        return {
            "products": enriched_list,
            "summary": summary,
            "recommendations": recommendations
        }
    
    def _generate_summary(
        self, 
        products: List[Dict[str, Any]], 
        query: str, 
        intent: Dict[str, Any]
    ) -> str:
        """Generate AI summary of search results using Ollama"""
        
        # Simple fallback summary
        if not products:
            return f"No products found matching '{query}'. Try different keywords or broader search terms."
        
        prompt = f"""You are a helpful shopping assistant. Summarize these search results for the user.

User Query: "{query}"
User Intent: {intent.get('intent', 'Find products')}

Found {len(products)} products. Here are the top 3:

"""
        for i, product in enumerate(products[:3], 1):
            prompt += f"{i}. {product['name']}\n"
            prompt += f"   Price: ₹{product['price']:,.0f} (MRP: ₹{product['mrp']:,.0f}, {product['discount_percent']}% off)\n"
            prompt += f"   Rating: {product['rating']}⭐ ({product['review_count']} reviews)\n"
            
            # Add key specifications if available
            if product.get('key_specs'):
                prompt += f"   Key Specs: {', '.join(product['key_specs'][:4])}\n"
            
            prompt += f"   Features: {', '.join(product['features'][:3])}\n\n"
        
        prompt += """Provide a helpful 2-3 sentence summary:
1. What products were found
2. Price range and best deals
3. One key recommendation

Keep it conversational and helpful. Maximum 3 sentences."""

        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'num_predict': 150  # Limit response length
                }
            )
            return response['response'].strip()
        except Exception as e:
            print(f"Ollama Summary (using fallback): {e}")
            return f"Found {len(products)} products matching '{query}'. Top pick: {products[0]['name']} at ₹{products[0]['price']:,.0f} with {products[0]['rating']}⭐ rating."
    
    def _format_specifications(self, specs: Dict[str, Any]) -> List[str]:
        """Format specifications into readable key points"""
        
        if not specs:
            return []
        
        formatted = []
        
        # Mapping of spec keys to user-friendly labels
        spec_labels = {
            # Mobile/Electronics
            'processor': 'Processor',
            'ram': 'RAM',
            'storage': 'Storage',
            'camera': 'Camera',
            'front_camera': 'Front Camera',
            'battery': 'Battery',
            'battery_capacity': 'Battery',
            'battery_life': 'Battery Life',
            'screen_size': 'Screen',
            'display': 'Display',
            'os': 'OS',
            
            # Audio
            'driver_size': 'Driver',
            'impedance': 'Impedance',
            'connectivity': 'Connectivity',
            'charging_time': 'Charging',
            'noise_cancellation': 'Noise Cancellation',
            
            # Fashion
            'material': 'Material',
            'fit': 'Fit',
            'pattern': 'Pattern',
            'sleeve': 'Sleeve',
            
            # Home & Kitchen
            'capacity': 'Capacity',
            'power': 'Power',
            'dimensions': 'Dimensions',
            'weight': 'Weight',
            'warranty': 'Warranty'
        }
        
        # Format each specification
        for key, value in specs.items():
            if value and str(value).strip():
                label = spec_labels.get(key.lower(), key.replace('_', ' ').title())
                formatted.append(f"{label}: {value}")
        
        return formatted
    
    def _generate_recommendations(
        self, 
        products: List[Dict[str, Any]], 
        query: str
    ) -> List[str]:
        """Generate personalized recommendations"""
        
        if not products:
            return []
        
        recommendations = []
        
        # Best value recommendation
        if len(products) >= 2:
            best_value = min(products, key=lambda p: p['price'] / max(p['rating'], 1))
            recommendations.append(f"Best Value: {best_value['name']} - Great features at ₹{best_value['price']:,.0f}")
        
        # Highest rated recommendation
        highest_rated = max(products, key=lambda p: p['rating'])
        if highest_rated['rating'] >= 4.0:
            recommendations.append(f"Top Rated: {highest_rated['name']} - {highest_rated['rating']}⭐ with {highest_rated['review_count']} reviews")
        
        # Best discount recommendation
        best_discount = max(products, key=lambda p: p['discount_percent'])
        if best_discount['discount_percent'] > 10:
            recommendations.append(f"Best Deal: {best_discount['name']} - {best_discount['discount_percent']}% off!")
        
        return recommendations[:3]
    
    def get_product_details(self, product_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific product with AI insights
        
        Args:
            product_id: Product ID
            
        Returns:
            Dictionary with product details and AI analysis
        """
        db = next(get_db())
        
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return {
                    "success": False,
                    "error": "Product not found"
                }
            
            # Get related data
            reviews = db.query(Review).filter(Review.product_id == product_id).limit(10).all()
            price_history = db.query(PriceHistory).filter(
                PriceHistory.product_id == product_id
            ).order_by(PriceHistory.recorded_at.desc()).limit(30).all()
            offers = db.query(CardOffer).filter(CardOffer.product_id == product_id).all()
            
            # Parse features and specs
            try:
                features = json.loads(product.features) if product.features else []
            except:
                features = []
            
            try:
                specs = json.loads(product.specifications) if product.specifications else {}
            except:
                specs = {}
            
            # Build response
            result = {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "model": product.model,
                    "category": product.category,
                    "subcategory": product.subcategory,
                    "price": float(product.price),
                    "mrp": float(product.mrp) if product.mrp else float(product.price),
                    "discount_percent": round(((float(product.mrp or product.price) - float(product.price)) / float(product.mrp or product.price)) * 100, 1) if product.mrp else 0,
                    "rating": float(product.rating),
                    "review_count": product.review_count,
                    "description": product.description,
                    "features": features,
                    "specifications": specs
                },
                "reviews": [
                    {
                        "rating": r.rating,
                        "text": r.review_text,
                        "verified": r.verified_purchase
                    }
                    for r in reviews
                ],
                "price_history": [
                    {
                        "price": float(h.price),
                        "date": h.recorded_at.isoformat()
                    }
                    for h in price_history
                ],
                "offers": [
                    {
                        "bank": o.bank_name,
                        "type": o.offer_type,
                        "discount_percent": float(o.discount_percent) if o.discount_percent else None,
                        "cashback_amount": float(o.cashback_amount) if o.cashback_amount else None,
                        "emi_months": o.emi_months,
                        "emi_amount": float(o.emi_amount) if o.emi_amount else None
                    }
                    for o in offers
                ]
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
