# src/services/cache_manager.py
"""
Production-ready caching system for performance optimization
"""

from typing import Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import json
import hashlib

# Simple in-memory cache (In production, use Redis)
_cache = {}
_cache_timestamps = {}

class CacheManager:
    """Cache manager for recommendation system"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        params_str = json.dumps(kwargs, sort_keys=True)
        hash_suffix = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{hash_suffix}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in _cache:
            # Check if expired
            if key in _cache_timestamps:
                if datetime.utcnow() > _cache_timestamps[key]:
                    # Expired
                    del _cache[key]
                    del _cache_timestamps[key]
                    return None
            return _cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        _cache[key] = value
        ttl = ttl or self.default_ttl
        _cache_timestamps[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in _cache:
            del _cache[key]
        if key in _cache_timestamps:
            del _cache_timestamps[key]
    
    def clear_all(self):
        """Clear entire cache"""
        _cache.clear()
        _cache_timestamps.clear()
    
    def clear_prefix(self, prefix: str):
        """Clear all keys with given prefix"""
        keys_to_delete = [k for k in _cache.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            self.delete(key)

# Global cache instance
cache = CacheManager()

def cached(prefix: str, ttl: int = 300):
    """
    Decorator for caching function results
    
    Usage:
        @cached(prefix='recommendations', ttl=600)
        def get_recommendations(user_id):
            # expensive operation
            return results
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(prefix, args=args, kwargs=kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user"""
    cache.clear_prefix(f'user:{user_id}')
    cache.clear_prefix(f'recommendations:user:{user_id}')

def invalidate_product_cache(product_id: int):
    """Invalidate all cache entries for a product"""
    cache.clear_prefix(f'product:{product_id}')
