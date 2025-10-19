"""
Redis caching service for VGM Website
Provides caching for sessions, prayer times, mosque lists, and other frequently accessed data
"""

import redis
import json
import os
from typing import Any, Optional, Dict, List
from datetime import timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service"""
    
    def __init__(self):
        self.redis_url = os.environ.get('REDIS_URL')
        self.redis_client = None
        
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis_client = None
        else:
            logger.info("Redis not configured, caching disabled")
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self.redis_client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_available():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set value in cache with TTL"""
        if not self.is_available():
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl_seconds, serialized)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, func, ttl_seconds: int = 3600) -> Any:
        """Get from cache or set using function"""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        # Generate value using function
        value = func()
        self.set(key, value, ttl_seconds)
        return value

# Global cache instance
cache = CacheService()

def cached(ttl_seconds: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """Invalidate cache entries matching pattern"""
    return cache.delete_pattern(pattern)

# Cache key constants
class CacheKeys:
    MOSQUES_LIST = "mosques:list"
    MOSQUE_DETAIL = "mosque:detail:{mosque_id}"
    EVENTS_LIST = "events:list"
    EVENTS_MOSQUE = "events:mosque:{mosque_id}"
    NEWS_LIST = "news:list"
    PRAYER_TIMES = "prayer_times:{mosque_id}:{date}"
    USER_SESSION = "user_session:{session_id}"
    ANALYTICS_SUMMARY = "analytics:summary"
    SEARCH_RESULTS = "search:{query}:{type}"

# Specific caching functions
def cache_mosques_list(mosques: List[Dict]) -> bool:
    """Cache mosque list for 1 hour"""
    return cache.set(CacheKeys.MOSQUES_LIST, mosques, 3600)

def get_cached_mosques_list() -> Optional[List[Dict]]:
    """Get cached mosque list"""
    return cache.get(CacheKeys.MOSQUES_LIST)

def cache_mosque_detail(mosque_id: int, mosque_data: Dict) -> bool:
    """Cache mosque detail for 1 hour"""
    key = CacheKeys.MOSQUE_DETAIL.format(mosque_id=mosque_id)
    return cache.set(key, mosque_data, 3600)

def get_cached_mosque_detail(mosque_id: int) -> Optional[Dict]:
    """Get cached mosque detail"""
    key = CacheKeys.MOSQUE_DETAIL.format(mosque_id=mosque_id)
    return cache.get(key)

def cache_prayer_times(mosque_id: int, date: str, prayer_times: Dict) -> bool:
    """Cache prayer times for 24 hours"""
    key = CacheKeys.PRAYER_TIMES.format(mosque_id=mosque_id, date=date)
    return cache.set(key, prayer_times, 86400)  # 24 hours

def get_cached_prayer_times(mosque_id: int, date: str) -> Optional[Dict]:
    """Get cached prayer times"""
    key = CacheKeys.PRAYER_TIMES.format(mosque_id=mosque_id, date=date)
    return cache.get(key)

def cache_user_session(session_id: str, user_data: Dict) -> bool:
    """Cache user session for 7 days"""
    key = CacheKeys.USER_SESSION.format(session_id=session_id)
    return cache.set(key, user_data, 604800)  # 7 days

def get_cached_user_session(session_id: str) -> Optional[Dict]:
    """Get cached user session"""
    key = CacheKeys.USER_SESSION.format(session_id=session_id)
    return cache.get(key)

def invalidate_mosque_cache(mosque_id: int = None):
    """Invalidate mosque-related cache"""
    if mosque_id:
        # Invalidate specific mosque cache
        cache.delete(CacheKeys.MOSQUE_DETAIL.format(mosque_id=mosque_id))
        cache.delete_pattern(f"events:mosque:{mosque_id}*")
        cache.delete_pattern(f"prayer_times:{mosque_id}*")
    else:
        # Invalidate all mosque-related cache
        cache.delete(CacheKeys.MOSQUES_LIST)
        cache.delete_pattern("mosque:detail:*")
        cache.delete_pattern("events:mosque:*")
        cache.delete_pattern("prayer_times:*")

def invalidate_events_cache():
    """Invalidate events cache"""
    cache.delete(CacheKeys.EVENTS_LIST)
    cache.delete_pattern("events:mosque:*")

def invalidate_news_cache():
    """Invalidate news cache"""
    cache.delete(CacheKeys.NEWS_LIST)

def invalidate_analytics_cache():
    """Invalidate analytics cache"""
    cache.delete(CacheKeys.ANALYTICS_SUMMARY)
