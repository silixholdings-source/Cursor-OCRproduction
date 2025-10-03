#!/usr/bin/env python3
"""
Production Redis Configuration for AI ERP SaaS
Handles caching, session management, and real-time features
"""

import os
import json
import asyncio
import aioredis
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

class ProductionRedis:
    """Production-grade Redis configuration"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.pool_size = int(os.getenv("REDIS_POOL_SIZE", "10"))
        self.redis_client = None
        
    async def connect(self):
        """Initialize Redis connection with proper configuration"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.pool_size,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def set_cache(self, key: str, value: Any, expire: int = 3600):
        """Set cache value with expiration"""
        if not self.redis_client:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis_client.setex(key, expire, value)
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """Delete cache value"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False
    
    async def set_session(self, session_id: str, user_data: Dict, expire: int = 1800):
        """Set user session data"""
        return await self.set_cache(f"session:{session_id}", user_data, expire)
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get user session data"""
        return await self.get_cache(f"session:{session_id}")
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete user session"""
        return await self.delete_cache(f"session:{session_id}")
    
    async def increment_rate_limit(self, client_ip: str, window: int = 60) -> int:
        """Increment rate limit counter"""
        if not self.redis_client:
            return 0
        
        try:
            pipe = self.redis_client.pipeline()
            key = f"rate_limit:{client_ip}"
            
            pipe.incr(key)
            pipe.expire(key, window)
            
            results = await pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Rate limit increment failed: {e}")
            return 0
    
    async def get_health_status(self) -> Dict:
        """Get Redis health and performance metrics"""
        if not self.redis_client:
            return {"status": "disconnected"}
        
        try:
            # Test connection
            ping_start = asyncio.get_event_loop().time()
            await self.redis_client.ping()
            ping_time = (asyncio.get_event_loop().time() - ping_start) * 1000
            
            # Get Redis info
            info = await self.redis_client.info()
            
            return {
                "status": "connected",
                "ping_time_ms": round(ping_time, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "version": info.get("redis_version", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Global Redis instance
production_redis = ProductionRedis()
