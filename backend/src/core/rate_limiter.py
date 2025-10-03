"""
Advanced Rate Limiting System
Implements multiple rate limiting strategies for enterprise security
"""
import time
import json
from typing import Optional, Dict, Any, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
from .config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.strategies = {
            "fixed_window": self._fixed_window_limit,
            "sliding_window": self._sliding_window_limit,
            "token_bucket": self._token_bucket_limit,
            "leaky_bucket": self._leaky_bucket_limit
        }
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get user ID from JWT token first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, decode JWT to get user ID
            # For now, use IP + user agent as fallback
            pass
        
        # Fallback to IP + User Agent
        ip_address = request.client.host
        user_agent = request.headers.get("User-Agent", "")
        return f"{ip_address}:{hash(user_agent)}"
    
    def _fixed_window_limit(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Fixed window rate limiting"""
        current_window = int(time.time() // window)
        window_key = f"rate_limit:fixed:{key}:{current_window}"
        
        current = self.redis_client.incr(window_key)
        if current == 1:
            self.redis_client.expire(window_key, window)
        
        return {
            "allowed": current <= limit,
            "limit": limit,
            "remaining": max(0, limit - current),
            "reset_time": (current_window + 1) * window,
            "current": current
        }
    
    def _sliding_window_limit(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Sliding window rate limiting"""
        now = time.time()
        window_start = now - window
        
        # Use sorted set to track requests
        zset_key = f"rate_limit:sliding:{key}"
        
        # Remove old entries
        self.redis_client.zremrangebyscore(zset_key, 0, window_start)
        
        # Count current requests
        current = self.redis_client.zcard(zset_key)
        
        if current < limit:
            # Add current request
            self.redis_client.zadd(zset_key, {str(now): now})
            self.redis_client.expire(zset_key, window)
            current += 1
        
        return {
            "allowed": current <= limit,
            "limit": limit,
            "remaining": max(0, limit - current),
            "reset_time": int(now + window),
            "current": current
        }
    
    def _token_bucket_limit(self, key: str, capacity: int, refill_rate: float) -> Dict[str, Any]:
        """Token bucket rate limiting"""
        bucket_key = f"rate_limit:bucket:{key}"
        now = time.time()
        
        # Get current bucket state
        bucket_data = self.redis_client.hgetall(bucket_key)
        
        if not bucket_data:
            # Initialize bucket
            tokens = capacity
            last_refill = now
        else:
            tokens = float(bucket_data.get(b"tokens", capacity))
            last_refill = float(bucket_data.get(b"last_refill", now))
        
        # Calculate tokens to add based on time passed
        time_passed = now - last_refill
        tokens_to_add = time_passed * refill_rate
        tokens = min(capacity, tokens + tokens_to_add)
        
        # Check if request can be processed
        if tokens >= 1:
            tokens -= 1
            allowed = True
        else:
            allowed = False
        
        # Update bucket state
        self.redis_client.hset(bucket_key, mapping={
            "tokens": tokens,
            "last_refill": now
        })
        self.redis_client.expire(bucket_key, 3600)  # 1 hour
        
        return {
            "allowed": allowed,
            "limit": capacity,
            "remaining": int(tokens),
            "reset_time": int(now + (capacity - tokens) / refill_rate),
            "current": int(capacity - tokens)
        }
    
    def _leaky_bucket_limit(self, key: str, capacity: int, leak_rate: float) -> Dict[str, Any]:
        """Leaky bucket rate limiting"""
        bucket_key = f"rate_limit:leaky:{key}"
        now = time.time()
        
        # Get current bucket state
        bucket_data = self.redis_client.hgetall(bucket_key)
        
        if not bucket_data:
            # Initialize bucket
            level = 0
            last_leak = now
        else:
            level = float(bucket_data.get(b"level", 0))
            last_leak = float(bucket_data.get(b"last_leak", now))
        
        # Calculate leaked amount
        time_passed = now - last_leak
        leaked = time_passed * leak_rate
        level = max(0, level - leaked)
        
        # Check if request can be processed
        if level < capacity:
            level += 1
            allowed = True
        else:
            allowed = False
        
        # Update bucket state
        self.redis_client.hset(bucket_key, mapping={
            "level": level,
            "last_leak": now
        })
        self.redis_client.expire(bucket_key, 3600)  # 1 hour
        
        return {
            "allowed": allowed,
            "limit": capacity,
            "remaining": max(0, capacity - int(level)),
            "reset_time": int(now + level / leak_rate),
            "current": int(level)
        }
    
    def check_rate_limit(self, request: Request, strategy: str = "sliding_window", 
                        **kwargs) -> Dict[str, Any]:
        """Check rate limit for request"""
        try:
            identifier = self._get_client_identifier(request)
            endpoint = request.url.path
            
            # Create unique key for this endpoint
            key = f"{identifier}:{endpoint}"
            
            # Get strategy function
            if strategy not in self.strategies:
                raise ValueError(f"Unknown rate limiting strategy: {strategy}")
            
            strategy_func = self.strategies[strategy]
            
            # Apply rate limiting
            result = strategy_func(key, **kwargs)
            
            # Add headers for client information
            result["headers"] = {
                "X-RateLimit-Limit": str(result["limit"]),
                "X-RateLimit-Remaining": str(result["remaining"]),
                "X-RateLimit-Reset": str(result["reset_time"]),
                "X-RateLimit-Strategy": strategy
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request if rate limiting fails
            return {
                "allowed": True,
                "limit": 1000,
                "remaining": 999,
                "reset_time": int(time.time() + 3600),
                "current": 1,
                "headers": {},
                "error": str(e)
            }
    
    def get_rate_limit_config(self, endpoint: str) -> Dict[str, Any]:
        """Get rate limit configuration for endpoint"""
        configs = {
            "/api/v1/auth/login": {
                "strategy": "fixed_window",
                "limit": 5,
                "window": 300  # 5 minutes
            },
            "/api/v1/auth/register": {
                "strategy": "fixed_window",
                "limit": 3,
                "window": 3600  # 1 hour
            },
            "/api/v1/processing/process": {
                "strategy": "token_bucket",
                "capacity": 10,
                "refill_rate": 1.0  # 1 request per second
            },
            "/api/v1/erp/": {
                "strategy": "sliding_window",
                "limit": 100,
                "window": 3600  # 1 hour
            },
            "default": {
                "strategy": "sliding_window",
                "limit": 1000,
                "window": 3600  # 1 hour
            }
        }
        
        # Find matching config
        for pattern, config in configs.items():
            if endpoint.startswith(pattern):
                return config
        
        return configs["default"]

# Global rate limiter instance
rate_limiter = RateLimiter()

class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/ready"]:
            await self.app(scope, receive, send)
            return
        
        # Get rate limit config
        config = rate_limiter.get_rate_limit_config(request.url.path)
        
        # Check rate limit
        result = rate_limiter.check_rate_limit(request, **config)
        
        if not result["allowed"]:
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {result['limit']}, "
                              f"Remaining: {result['remaining']}, "
                              f"Reset time: {result['reset_time']}",
                    "retry_after": result["reset_time"] - int(time.time())
                }
            )
            
            # Add rate limit headers
            for header, value in result["headers"].items():
                response.headers[header] = value
            
            await response(scope, receive, send)
            return
        
        # Add rate limit headers to successful responses
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                for header, value in result["headers"].items():
                    headers.append([header.encode(), str(value).encode()])
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
