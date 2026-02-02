# src/utils/cache.py
"""
Simple in-memory cache for agent results
Speeds up repeated queries and reduces database load
"""
from typing import Any, Optional
from datetime import datetime, timedelta
import threading

class SimpleCache:
    """Thread-safe in-memory cache with TTL"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default TTL
        self.cache = {}
        self.ttl = ttl_seconds
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                # Check if expired
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    return value
                else:
                    # Remove expired entry
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache with current timestamp"""
        with self.lock:
            self.cache[key] = (value, datetime.now())
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
    
    def remove(self, key: str):
        """Remove specific key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]

# Global cache instances for different agents
review_cache = SimpleCache(ttl_seconds=600)  # 10 minutes for reviews
comparison_cache = SimpleCache(ttl_seconds=300)  # 5 minutes for comparisons
price_cache = SimpleCache(ttl_seconds=180)  # 3 minutes for prices
