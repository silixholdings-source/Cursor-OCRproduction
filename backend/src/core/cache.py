"""
Advanced Caching System
Implements multi-level caching with Redis, in-memory, and CDN support
"""
import json
import pickle
import hashlib
import time
from typing import Any, Optional, Dict, List, Callable, Union
from datetime import datetime, timedelta
from functools import wraps
import redis
from .config import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Advanced cache management system"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.memory_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        self.default_ttl = 3600  # 1 hour
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate cache key with namespace"""
        return f"{namespace}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON first for simple types
            return json.dumps(value).encode()
        except (TypeError, ValueError):
            # Fall back to pickle for complex types
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache"""
        try:
            cache_key = self._generate_key(key, namespace)
            
            # Try memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if entry["expires_at"] > time.time():
                    self.cache_stats["hits"] += 1
                    return entry["value"]
                else:
                    # Expired, remove from memory
                    del self.memory_cache[cache_key]
            
            # Try Redis cache
            data = self.redis_client.get(cache_key)
            if data:
                value = self._deserialize_value(data)
                # Store in memory cache for faster access
                self.memory_cache[cache_key] = {
                    "value": value,
                    "expires_at": time.time() + 300  # 5 minutes in memory
                }
                self.cache_stats["hits"] += 1
                return value
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            namespace: str = "default") -> bool:
        """Set value in cache"""
        try:
            cache_key = self._generate_key(key, namespace)
            serialized_value = self._serialize_value(value)
            ttl = ttl or self.default_ttl
            
            # Store in Redis
            success = self.redis_client.setex(cache_key, ttl, serialized_value)
            
            if success:
                # Store in memory cache
                self.memory_cache[cache_key] = {
                    "value": value,
                    "expires_at": time.time() + min(ttl, 300)  # Max 5 minutes in memory
                }
                self.cache_stats["sets"] += 1
            
            return bool(success)
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache"""
        try:
            cache_key = self._generate_key(key, namespace)
            
            # Delete from Redis
            redis_deleted = self.redis_client.delete(cache_key)
            
            # Delete from memory cache
            memory_deleted = cache_key in self.memory_cache
            if memory_deleted:
                del self.memory_cache[cache_key]
            
            if redis_deleted or memory_deleted:
                self.cache_stats["deletes"] += 1
            
            return bool(redis_deleted or memory_deleted)
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in cache"""
        try:
            cache_key = self._generate_key(key, namespace)
            
            # Check memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if entry["expires_at"] > time.time():
                    return True
                else:
                    del self.memory_cache[cache_key]
            
            # Check Redis cache
            return bool(self.redis_client.exists(cache_key))
            
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace"""
        try:
            pattern = f"{namespace}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                
                # Clear from memory cache
                memory_keys = [k for k in self.memory_cache.keys() if k.startswith(f"{namespace}:")]
                for key in memory_keys:
                    del self.memory_cache[key]
                
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear namespace error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": round(hit_rate, 2),
            "memory_cache_size": len(self.memory_cache),
            "redis_info": self.redis_client.info()
        }

class CacheDecorator:
    """Cache decorator for functions"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def cache(self, ttl: int = 3600, namespace: str = "default", 
              key_func: Optional[Callable] = None):
        """Cache decorator for functions"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                    cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try to get from cache
                cached_result = self.cache_manager.get(cache_key, namespace)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.cache_manager.set(cache_key, result, ttl, namespace)
                return result
            
            return wrapper
        return decorator
    
    def cache_invalidate(self, pattern: str, namespace: str = "default"):
        """Invalidate cache entries matching pattern"""
        try:
            keys = self.cache_manager.redis_client.keys(f"{namespace}:{pattern}")
            if keys:
                return self.cache_manager.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0

class QueryCache:
    """Database query caching system"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.query_stats = {
            "cached_queries": 0,
            "missed_queries": 0,
            "invalidated_queries": 0
        }
    
    def cache_query(self, query_key: str, result: Any, ttl: int = 1800) -> bool:
        """Cache database query result"""
        try:
            success = self.cache_manager.set(
                f"query:{query_key}",
                result,
                ttl,
                "database"
            )
            if success:
                self.query_stats["cached_queries"] += 1
            return success
        except Exception as e:
            logger.error(f"Query cache error: {e}")
            return False
    
    def get_cached_query(self, query_key: str) -> Optional[Any]:
        """Get cached query result"""
        try:
            result = self.cache_manager.get(f"query:{query_key}", "database")
            if result is not None:
                self.query_stats["cached_queries"] += 1
            else:
                self.query_stats["missed_queries"] += 1
            return result
        except Exception as e:
            logger.error(f"Query cache get error: {e}")
            self.query_stats["missed_queries"] += 1
            return None
    
    def invalidate_table_cache(self, table_name: str) -> int:
        """Invalidate all cached queries for a table"""
        try:
            pattern = f"query:*:{table_name}:*"
            deleted = self.cache_manager.redis_client.delete(
                *self.cache_manager.redis_client.keys(pattern)
            )
            self.query_stats["invalidated_queries"] += deleted
            return deleted
        except Exception as e:
            logger.error(f"Table cache invalidation error: {e}")
            return 0
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query cache statistics"""
        return self.query_stats.copy()

class SessionCache:
    """User session caching system"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.session_ttl = 1800  # 30 minutes
    
    def store_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Store user session data"""
        try:
            return self.cache_manager.set(
                f"session:{session_id}",
                user_data,
                self.session_ttl,
                "sessions"
            )
        except Exception as e:
            logger.error(f"Session store error: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        try:
            return self.cache_manager.get(f"session:{session_id}", "sessions")
        except Exception as e:
            logger.error(f"Session get error: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete user session"""
        try:
            return self.cache_manager.delete(f"session:{session_id}", "sessions")
        except Exception as e:
            logger.error(f"Session delete error: {e}")
            return False
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session TTL"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                return self.store_session(session_id, session_data)
            return False
        except Exception as e:
            logger.error(f"Session extend error: {e}")
            return False

class CDNCache:
    """CDN cache management system"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.cdn_endpoints = {
            "static": "https://cdn.example.com/static",
            "images": "https://cdn.example.com/images",
            "api": "https://cdn.example.com/api"
        }
    
    def get_cdn_url(self, path: str, endpoint: str = "static") -> str:
        """Get CDN URL for a resource"""
        base_url = self.cdn_endpoints.get(endpoint, self.cdn_endpoints["static"])
        return f"{base_url}/{path.lstrip('/')}"
    
    def invalidate_cdn_cache(self, path: str, endpoint: str = "static") -> bool:
        """Invalidate CDN cache for a resource"""
        try:
            # In a real implementation, this would call CDN API
            # For now, just log the invalidation
            logger.info(f"CDN cache invalidation requested for {endpoint}/{path}")
            return True
        except Exception as e:
            logger.error(f"CDN cache invalidation error: {e}")
            return False
    
    def preload_resource(self, path: str, endpoint: str = "static") -> bool:
        """Preload resource to CDN cache"""
        try:
            # In a real implementation, this would call CDN API
            logger.info(f"CDN preload requested for {endpoint}/{path}")
            return True
        except Exception as e:
            logger.error(f"CDN preload error: {e}")
            return False

# Global cache instances
cache_manager = CacheManager()
cache_decorator = CacheDecorator(cache_manager)
query_cache = QueryCache(cache_manager)
session_cache = SessionCache(cache_manager)
cdn_cache = CDNCache(cache_manager)

# Convenience functions
def cache(ttl: int = 3600, namespace: str = "default", key_func: Optional[Callable] = None):
    """Convenience function for cache decorator"""
    return cache_decorator.cache(ttl, namespace, key_func)

def cache_invalidate(pattern: str, namespace: str = "default"):
    """Convenience function for cache invalidation"""
    return cache_decorator.cache_invalidate(pattern, namespace)
