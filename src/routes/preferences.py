# src/routes/preferences.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.database.connection import get_db
from src.database.models import Wishlist, SearchHistory, Product, User
from src.utils.middleware import get_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])

# ============================================================================
# Pydantic Models
# ============================================================================

class WishlistItemCreate(BaseModel):
    product_id: int
    notes: Optional[str] = None

class WishlistItemUpdate(BaseModel):
    notes: Optional[str] = None

class WishlistItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    notes: Optional[str]
    added_at: datetime
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    product_image: Optional[str] = None
    product_rating: Optional[float] = None
    in_stock: Optional[bool] = None

    class Config:
        from_attributes = True

class SearchHistoryCreate(BaseModel):
    query: str
    results_count: Optional[int] = 0
    clicked_product_id: Optional[int] = None

class SearchHistoryResponse(BaseModel):
    id: int
    user_id: Optional[int]
    query: str
    results_count: Optional[int]
    clicked_product_id: Optional[int]
    search_timestamp: datetime
    product_name: Optional[str] = None

    class Config:
        from_attributes = True

class UserPreferencesStats(BaseModel):
    wishlist_count: int
    search_history_count: int
    favorite_categories: List[str]
    recent_searches: List[str]

# ============================================================================
# Wishlist Endpoints
# ============================================================================

@router.post("/wishlist", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    item: WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a product to user's wishlist.
    
    - **product_id**: ID of the product to add
    - **notes**: Optional notes about the product
    """
    # Check if product exists
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already in wishlist
    existing_item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == item.product_id
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in wishlist"
        )
    
    # Create wishlist item
    wishlist_item = Wishlist(
        user_id=current_user.id,
        product_id=item.product_id,
        notes=item.notes
    )
    
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    
    # Add product details to response
    response = WishlistItemResponse(
        id=wishlist_item.id,
        user_id=wishlist_item.user_id,
        product_id=wishlist_item.product_id,
        notes=wishlist_item.notes,
        added_at=wishlist_item.added_at,
        product_name=product.name,
        product_price=product.price,
        product_image=product.image_url,
        product_rating=product.rating,
        in_stock=product.in_stock
    )
    
    return response

@router.get("/wishlist", response_model=List[WishlistItemResponse])
async def get_wishlist(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's wishlist items.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return
    """
    wishlist_items = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).order_by(Wishlist.added_at.desc()).offset(skip).limit(limit).all()
    
    # Enrich with product details
    response = []
    for item in wishlist_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        response.append(WishlistItemResponse(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            notes=item.notes,
            added_at=item.added_at,
            product_name=product.name if product else None,
            product_price=product.price if product else None,
            product_image=product.image_url if product else None,
            product_rating=product.rating if product else None,
            in_stock=product.in_stock if product else None
        ))
    
    return response

@router.get("/wishlist/{item_id}", response_model=WishlistItemResponse)
async def get_wishlist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific wishlist item by ID."""
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.id == item_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    product = db.query(Product).filter(Product.id == wishlist_item.product_id).first()
    
    return WishlistItemResponse(
        id=wishlist_item.id,
        user_id=wishlist_item.user_id,
        product_id=wishlist_item.product_id,
        notes=wishlist_item.notes,
        added_at=wishlist_item.added_at,
        product_name=product.name if product else None,
        product_price=product.price if product else None,
        product_image=product.image_url if product else None,
        product_rating=product.rating if product else None,
        in_stock=product.in_stock if product else None
    )

@router.put("/wishlist/{item_id}", response_model=WishlistItemResponse)
async def update_wishlist_item(
    item_id: int,
    update: WishlistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notes for a wishlist item."""
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.id == item_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    if update.notes is not None:
        wishlist_item.notes = update.notes
    
    db.commit()
    db.refresh(wishlist_item)
    
    product = db.query(Product).filter(Product.id == wishlist_item.product_id).first()
    
    return WishlistItemResponse(
        id=wishlist_item.id,
        user_id=wishlist_item.user_id,
        product_id=wishlist_item.product_id,
        notes=wishlist_item.notes,
        added_at=wishlist_item.added_at,
        product_name=product.name if product else None,
        product_price=product.price if product else None,
        product_image=product.image_url if product else None,
        product_rating=product.rating if product else None,
        in_stock=product.in_stock if product else None
    )

@router.delete("/wishlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a product from wishlist."""
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.id == item_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    db.delete(wishlist_item)
    db.commit()
    
    return None

@router.delete("/wishlist/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a product from wishlist by product ID."""
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.product_id == product_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in wishlist"
        )
    
    db.delete(wishlist_item)
    db.commit()
    
    return None

@router.get("/wishlist/check/{product_id}")
async def check_in_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if a product is in the user's wishlist."""
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.product_id == product_id,
        Wishlist.user_id == current_user.id
    ).first()
    
    return {
        "in_wishlist": wishlist_item is not None,
        "wishlist_item_id": wishlist_item.id if wishlist_item else None
    }

# ============================================================================
# Search History Endpoints
# ============================================================================

@router.post("/search-history", response_model=SearchHistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_search_history(
    search: SearchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a search in user's history.
    
    - **query**: Search query text
    - **results_count**: Number of results returned
    - **clicked_product_id**: Product ID if user clicked on a result
    """
    search_entry = SearchHistory(
        user_id=current_user.id,
        query=search.query,
        results_count=search.results_count,
        clicked_product_id=search.clicked_product_id
    )
    
    db.add(search_entry)
    db.commit()
    db.refresh(search_entry)
    
    # Get product name if clicked
    product_name = None
    if search_entry.clicked_product_id:
        product = db.query(Product).filter(Product.id == search_entry.clicked_product_id).first()
        product_name = product.name if product else None
    
    return SearchHistoryResponse(
        id=search_entry.id,
        user_id=search_entry.user_id,
        query=search_entry.query,
        results_count=search_entry.results_count,
        clicked_product_id=search_entry.clicked_product_id,
        search_timestamp=search_entry.search_timestamp,
        product_name=product_name
    )

@router.get("/search-history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's search history.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return
    """
    history = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(SearchHistory.search_timestamp.desc()).offset(skip).limit(limit).all()
    
    # Enrich with product names
    response = []
    for entry in history:
        product_name = None
        if entry.clicked_product_id:
            product = db.query(Product).filter(Product.id == entry.clicked_product_id).first()
            product_name = product.name if product else None
        
        response.append(SearchHistoryResponse(
            id=entry.id,
            user_id=entry.user_id,
            query=entry.query,
            results_count=entry.results_count,
            clicked_product_id=entry.clicked_product_id,
            search_timestamp=entry.search_timestamp,
            product_name=product_name
        ))
    
    return response

@router.delete("/search-history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific search history entry."""
    history_item = db.query(SearchHistory).filter(
        SearchHistory.id == history_id,
        SearchHistory.user_id == current_user.id
    ).first()
    
    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search history item not found"
        )
    
    db.delete(history_item)
    db.commit()
    
    return None

@router.delete("/search-history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear all search history for the current user."""
    db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return None

# ============================================================================
# User Preferences & Stats
# ============================================================================

@router.get("/stats", response_model=UserPreferencesStats)
async def get_user_preferences_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user preferences statistics and insights."""
    
    # Count wishlist items
    wishlist_count = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).count()
    
    # Count search history
    search_history_count = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).count()
    
    # Get favorite categories (from wishlist)
    wishlist_items = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).all()
    
    category_count = {}
    for item in wishlist_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product and product.category:
            category_count[product.category] = category_count.get(product.category, 0) + 1
    
    # Sort by count and get top 5
    favorite_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)
    favorite_categories = [cat for cat, count in favorite_categories[:5]]
    
    # Get recent searches (last 10)
    recent_searches_query = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(SearchHistory.search_timestamp.desc()).limit(10).all()
    
    recent_searches = [entry.query for entry in recent_searches_query]
    
    return UserPreferencesStats(
        wishlist_count=wishlist_count,
        search_history_count=search_history_count,
        favorite_categories=favorite_categories,
        recent_searches=recent_searches
    )
