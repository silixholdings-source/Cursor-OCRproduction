"""
Advanced Rate Limiting System
Provides sophisticated rate limiting with multiple strategies and Redis backend
"""
import time
import json
import logging
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from fastapi import Request, HTTPException, status
from .config import settings

logger = logging.getLogger(__name__)

class RateLimitStrategy:
    """Base class for rate limiting strategies"""
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
    
    async def is_allowed(self, key: str, redis_client: redis.Redis) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed under this strategy"""
        raise NotImplementedError

class FixedWindowStrategy(RateLimitStrategy):
    """Fixed window rate limiting strategy"""
    
    async def is_allowed(self, key: str, redis_client: redis.Redis) -> Tuple[bool, Dict[str, Any]]:
        current_window = int(time.time() // self.window)
        window_key = f"rate_limit:{key}:{current_window}"
        
        try:
            current_count = await redis_client.get(window_key)
            if current_count is None:
                await redis_client.setex(window_key, self.window, 1)
                return True, {
                    "limit": self.limit,
                    "remaining": self.limit - 1,
                    "reset_time": (current_window + 1) * self.window
                }
            
            current_count = int(current_count)
            if current_count >= self.limit:
                return False, {
                    "limit": self.limit,
                    "remaining": 0,
                    "reset_time": (current_window + 1) * self.window
                }
            
            await redis_client.incr(window_key)
            return True, {
                "limit": self.limit,
                "remaining": self.limit - current_count - 1,
                "reset_time": (current_window + 1) * self.window
            }
        except Exception as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Allow request if Redis is down (fail open)
            return True, {"limit": self.limit, "remaining": self.limit, "reset_time": int(time.time()) + self.window}

class SlidingWindowStrategy(RateLimitStrategy):
    """Sliding window rate limiting strategy"""
    
    async def is_allowed(self, key: str, redis_client: redis.Redis) -> Tuple[bool, Dict[str, Any]]:
        now = time.time()
        window_start = now - self.window
        
        try:
            # Use sorted set to track requests
            sorted_set_key = f"rate_limit_sliding:{key}"
            
            # Remove old entries
            await redis_client.zremrangebyscore(sorted_set_key, 0, window_start)
            
            # Count current requests
            current_count = await redis_client.zcard(sorted_set_key)
            
            if current_count >= self.limit:
                # Get oldest request time for reset calculation
                oldest_request = await redis_client.zrange(sorted_set_key, 0, 0, withscores=True)
                reset_time = int(oldest_request[0][1] + self.window) if oldest_request else int(now + self.window)
                
                return False, {
                    "limit": self.limit,
                    "remaining": 0,
                    "reset_time": reset_time
                }
            
            # Add current request
            await redis_client.zadd(sorted_set_key, {str(now): now})
            await redis_client.expire(sorted_set_key, self.window)
            
            return True, {
                "limit": self.limit,
                "remaining": self.limit - current_count - 1,
                "reset_time": int(now + self.window)
            }
        except Exception as e:
            logger.error(f"Redis error in sliding window rate limiting: {e}")
            return True, {"limit": self.limit, "remaining": self.limit, "reset_time": int(now + self.window)}

class TokenBucketStrategy(RateLimitStrategy):
    """Token bucket rate limiting strategy"""
    
    def __init__(self, limit: int, window: int, refill_rate: float = None):
        super().__init__(limit, window)
        self.refill_rate = refill_rate or (limit / window)  # tokens per second
    
    async def is_allowed(self, key: str, redis_client: redis.Redis) -> Tuple[bool, Dict[str, Any]]:
        now = time.time()
        bucket_key = f"rate_limit_bucket:{key}"
        
        try:
            # Get bucket state
            bucket_data = await redis_client.get(bucket_key)
            
            if bucket_data is None:
                # Initialize bucket
                bucket_state = {
                    "tokens": self.limit,
                    "last_refill": now
                }
            else:
                bucket_state = json.loads(bucket_data)
                # Refill tokens based on time passed
                time_passed = now - bucket_state["last_refill"]
                tokens_to_add = time_passed * self.refill_rate
                bucket_state["tokens"] = min(self.limit, bucket_state["tokens"] + tokens_to_add)
                bucket_state["last_refill"] = now
            
            if bucket_state["tokens"] >= 1:
                # Consume token
                bucket_state["tokens"] -= 1
                await redis_client.setex(bucket_key, self.window, json.dumps(bucket_state))
                
                return True, {
                    "limit": self.limit,
                    "remaining": int(bucket_state["tokens"]),
                    "reset_time": int(now + (1 - bucket_state["tokens"]) / self.refill_rate)
                }
            else:
                # No tokens available
                time_until_refill = (1 - bucket_state["tokens"]) / self.refill_rate
                return False, {
                    "limit": self.limit,
                    "remaining": 0,
                    "reset_time": int(now + time_until_refill)
                }
        except Exception as e:
            logger.error(f"Redis error in token bucket rate limiting: {e}")
            return True, {"limit": self.limit, "remaining": self.limit, "reset_time": int(now + self.window)}

class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies and Redis backend"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.strategies: Dict[str, RateLimitStrategy] = {}
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """Setup default rate limiting strategies"""
        # Global API limits
        self.strategies["global_api"] = FixedWindowStrategy(limit=1000, window=3600)  # 1000/hour
        self.strategies["global_api_per_minute"] = FixedWindowStrategy(limit=100, window=60)  # 100/minute
        
        # Authentication endpoints
        self.strategies["auth_login"] = FixedWindowStrategy(limit=5, window=300)  # 5/5min
        self.strategies["auth_register"] = FixedWindowStrategy(limit=3, window=3600)  # 3/hour
        
        # OCR processing
        self.strategies["ocr_processing"] = TokenBucketStrategy(limit=50, window=3600, refill_rate=0.02)  # 50/hour, 1 per 50s
        self.strategies["ocr_batch"] = FixedWindowStrategy(limit=10, window=3600)  # 10 batch jobs/hour
        
        # ERP integration
        self.strategies["erp_sync"] = SlidingWindowStrategy(limit=20, window=3600)  # 20/hour sliding
        
        # User-specific limits
        self.strategies["user_api"] = FixedWindowStrategy(limit=500, window=3600)  # 500/hour per user
        self.strategies["user_uploads"] = FixedWindowStrategy(limit=100, window=3600)  # 100 uploads/hour
        
        # Contact form limits
        self.strategies["contact_form"] = FixedWindowStrategy(limit=3, window=3600)  # 3 submissions/hour per IP
        self.strategies["contact_form_daily"] = FixedWindowStrategy(limit=10, window=86400)  # 10 submissions/day per IP
    
    def add_strategy(self, name: str, strategy: RateLimitStrategy):
        """Add a custom rate limiting strategy"""
        self.strategies[name] = strategy
    
    def get_strategy(self, name: str) -> Optional[RateLimitStrategy]:
        """Get a rate limiting strategy by name"""
        return self.strategies.get(name)
    
    def _get_rate_limit_key(self, request: Request, strategy_name: str) -> str:
        """Generate rate limit key for the request"""
        # Try to get user ID from request state
        user_id = getattr(request.state, "user_id", None)
        company_id = getattr(request.state, "company_id", None)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Generate key based on strategy type
        if "user_" in strategy_name and user_id:
            return f"{strategy_name}:user:{user_id}"
        elif "company_" in strategy_name and company_id:
            return f"{strategy_name}:company:{company_id}"
        elif "global_" in strategy_name:
            return f"{strategy_name}:global"
        else:
            # Fall back to IP-based limiting
            return f"{strategy_name}:ip:{client_ip}"
    
    async def check_rate_limit(self, request: Request, strategy_name: str) -> Dict[str, Any]:
        """Check if request is allowed under the specified strategy"""
        if not self.redis_client:
            # No Redis available - allow all requests (fail open)
            logger.warning("Redis not available for rate limiting - allowing request")
            return {
                "allowed": True,
                "limit": 1000,
                "remaining": 999,
                "reset_time": int(time.time()) + 3600
            }
        
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            logger.warning(f"Unknown rate limit strategy: {strategy_name}")
            return {"allowed": True, "limit": 1000, "remaining": 999, "reset_time": int(time.time()) + 3600}
        
        key = self._get_rate_limit_key(request, strategy_name)
        allowed, info = await strategy.is_allowed(key, self.redis_client)
        
        return {
            "allowed": allowed,
            "limit": info["limit"],
            "remaining": info["remaining"],
            "reset_time": info["reset_time"]
        }
    
    async def enforce_rate_limit(self, request: Request, strategy_name: str):
        """Enforce rate limit and raise exception if exceeded"""
        rate_limit_info = await self.check_rate_limit(request, strategy_name)
        
        if not rate_limit_info["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "limit": rate_limit_info["limit"],
                    "remaining": rate_limit_info["remaining"],
                    "reset_time": rate_limit_info["reset_time"]
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limit_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_limit_info["reset_time"])
                }
            )
        
        return rate_limit_info

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

def setup_rate_limiter(redis_client: redis.Redis):
    """Setup the global rate limiter with Redis client"""
    global rate_limiter
    rate_limiter = AdvancedRateLimiter(redis_client)

def rate_limit(strategy_name: str):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find request object in args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                await rate_limiter.enforce_rate_limit(request, strategy_name)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
