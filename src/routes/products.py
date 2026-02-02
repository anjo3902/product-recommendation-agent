"""
FastAPI routes for product search and recommendations
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from src.agents.product_search_agent import ProductSearchAgent


router = APIRouter(prefix="/api/products", tags=["Products"])

# Initialize agent
search_agent = ProductSearchAgent()


class SearchRequest(BaseModel):
    """Request model for product search"""
    query: str = Field(..., description="Natural language search query", min_length=1)
    category: Optional[str] = Field(None, description="Category filter (Smartphones, Laptops, Headphones)")
    min_price: Optional[float] = Field(None, description="Minimum price", ge=0)
    max_price: Optional[float] = Field(None, description="Maximum price", ge=0)
    min_rating: Optional[float] = Field(None, description="Minimum rating", ge=1, le=5)
    limit: int = Field(10, description="Maximum number of results", ge=1, le=50)


class SearchResponse(BaseModel):
    """Response model for product search"""
    success: bool
    query: str
    intent: dict
    total_results: int
    products: list
    ai_summary: str
    recommendations: list


@router.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Search products using natural language query
    
    **Example queries:**
    - "best gaming laptop under 80000"
    - "Samsung phone with good camera"
    - "wireless headphones for running"
    - "iPhone with best battery life"
    - "budget laptop for students"
    """
    result = search_agent.search_products(
        query=request.query,
        category=request.category,
        min_price=request.min_price,
        max_price=request.max_price,
        min_rating=request.min_rating,
        limit=request.limit
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Search failed"))
    
    return result


@router.get("/search")
async def search_products_get(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    min_price: Optional[float] = Query(None, description="Minimum price", ge=0),
    max_price: Optional[float] = Query(None, description="Maximum price", ge=0),
    min_rating: Optional[float] = Query(None, description="Minimum rating", ge=1, le=5),
    limit: int = Query(10, description="Maximum results", ge=1, le=50)
):
    """
    Search products using GET request (alternative to POST)
    """
    result = search_agent.search_products(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        limit=limit
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Search failed"))
    
    return result


@router.get("/{product_id}")
async def get_product_details(product_id: int):
    """
    Get detailed information about a specific product
    
    **Returns:**
    - Product details
    - Recent reviews
    - Price history (last 30 days)
    - Available card offers
    """
    result = search_agent.get_product_details(product_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404 if "not found" in result.get("error", "").lower() else 500,
            detail=result.get("error", "Failed to get product details")
        )
    
    return result


@router.get("/")
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price", ge=0),
    max_price: Optional[float] = Query(None, description="Maximum price", ge=0),
    min_rating: Optional[float] = Query(None, description="Minimum rating", ge=1, le=5),
    limit: int = Query(20, description="Maximum results", ge=1, le=100),
    offset: int = Query(0, description="Results offset", ge=0)
):
    """
    List products with optional filters (no AI, direct database query)
    """
    from src.database.connection import get_db
    from src.database.models import Product
    from sqlalchemy import and_
    import json
    
    db = next(get_db())
    
    try:
        query = db.query(Product)
        
        filters = []
        if category:
            filters.append(Product.category == category)
        if brand:
            filters.append(Product.brand.ilike(f"%{brand}%"))
        if min_price:
            filters.append(Product.price >= min_price)
        if max_price:
            filters.append(Product.price <= max_price)
        if min_rating:
            filters.append(Product.rating >= min_rating)
        
        if filters:
            query = query.filter(and_(*filters))
        
        total = query.count()
        products = query.order_by(Product.rating.desc()).offset(offset).limit(limit).all()
        
        product_list = []
        for product in products:
            try:
                features = json.loads(product.features) if product.features else []
            except:
                features = []
            
            product_list.append({
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "model": product.model,
                "category": product.category,
                "price": float(product.price),
                "mrp": float(product.mrp) if product.mrp else float(product.price),
                "rating": float(product.rating),
                "review_count": product.review_count,
                "features": features[:3]
            })
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "products": product_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
