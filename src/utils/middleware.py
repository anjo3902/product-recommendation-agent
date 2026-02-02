"""
Authentication Middleware for FastAPI

This module provides middleware functions for protecting routes
that require authentication.

For Beginners:
- Middleware = Code that runs before your route handlers
- Dependency = Reusable function that can be injected into routes
- Protected Route = Route that requires user to be logged in
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from src.database.connection import get_db
from src.database.models import User
from src.utils.auth import TokenManager

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    
    Use this in any route that requires authentication:
    
    @router.get("/protected")
    async def protected_route(user: User = Depends(get_current_user)):
        return {"message": f"Hello {user.username}!"}
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        User object if authenticated
        
    Raises:
        HTTPException if not authenticated
    """
    token = credentials.credentials
    
    # Decode and verify token
    user_id = TokenManager.decode_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise
    
    Use this for routes that work with or without authentication:
    
    @router.get("/products")
    async def list_products(user: Optional[User] = Depends(get_optional_user)):
        if user:
            return {"message": f"Hello {user.username}, here are products"}
        else:
            return {"message": "Hello guest, here are products"}
    
    Args:
        credentials: Optional Bearer token
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        user_id = TokenManager.decode_token(credentials.credentials)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            return user
    except Exception:
        pass
    
    return None


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin privileges
    
    Note: This requires adding an 'is_admin' field to your User model
    For now, this is a placeholder
    
    @router.delete("/users/{user_id}")
    async def delete_user(user: User = Depends(require_admin)):
        # Only admins can access this
        pass
    """
    # TODO: Add is_admin field to User model
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin privileges required"
    #     )
    return current_user


# Example: Custom permission checker
class Permission:
    """
    Permission checker for fine-grained access control
    
    Example:
        can_delete_product = Permission("delete:product")
        
        @router.delete("/products/{id}")
        async def delete_product(
            product_id: int,
            user: User = Depends(can_delete_product)
        ):
            # Only users with delete:product permission can access
            pass
    """
    
    def __init__(self, permission: str):
        self.permission = permission
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Check if user has required permission
        
        Note: This requires implementing a permissions system
        For now, all authenticated users have all permissions
        """
        # TODO: Implement permission checking
        # if self.permission not in current_user.permissions:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail=f"Permission required: {self.permission}"
        #     )
        return current_user
