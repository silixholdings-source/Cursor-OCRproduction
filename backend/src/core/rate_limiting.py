"""
Advanced Rate Limiting Implementation
Provides sophisticated rate limiting with Redis backend and multiple strategies
"""
import time
import json
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)}
        )

class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_limits = {
            "global": {"requests": 1000, "window": 3600},  # 1000 requests per hour
            "per_ip": {"requests": 100, "window": 3600},   # 100 requests per hour per IP
            "per_user": {"requests": 200, "window": 3600}, # 200 requests per hour per user
            "auth": {"requests": 10, "window": 300},       # 10 auth attempts per 5 minutes
            "upload": {"requests": 20, "window": 3600},    # 20 uploads per hour
        }
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit_type: str = "per_ip",
        custom_limits: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Check rate limit for a given key"""
        limits = custom_limits or self.default_limits.get(limit_type, self.default_limits["per_ip"])
        requests = limits["requests"]
        window = limits["window"]
        
        current_time = int(time.time())
        window_start = current_time - window
        
        # Use sliding window counter
        pipe = self.redis.pipeline()
        
        # Remove expired entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipe.expire(key, window)
        
        results = await pipe.execute()
        current_count = results[1]
        
        if current_count >= requests:
            # Calculate retry after
            oldest_request = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest_request:
                retry_after = int(oldest_request[0][1]) + window - current_time
            else:
                retry_after = window
            
            raise RateLimitExceeded(
                detail=f"Rate limit exceeded. {requests} requests per {window} seconds allowed.",
                retry_after=max(retry_after, 1)
            )
        
        return {
            "limit": requests,
            "remaining": requests - current_count - 1,
            "reset_time": current_time + window,
            "retry_after": 0
        }

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with multiple strategies"""
    
    def __init__(self, app, rate_limiter: Optional[AdvancedRateLimiter]):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/health"]:
            return await call_next(request)
        
        # Determine rate limit type based on endpoint
        limit_type = self._get_limit_type(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # If no rate limiter configured, bypass gracefully
        if self.rate_limiter is None:
            return await call_next(request)

        # Check rate limit
        try:
            rate_info = await self.rate_limiter.check_rate_limit(
                f"rate_limit:{limit_type}:{client_id}",
                limit_type
            )
        except RateLimitExceeded as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": "Rate limit exceeded",
                    "message": e.detail,
                    "retry_after": e.headers.get("Retry-After")
                },
                headers=e.headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers if available
        try:
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])  # type: ignore[name-defined]
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])  # type: ignore[name-defined]
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset_time"])  # type: ignore[name-defined]
        except Exception:
            # In case rate_info is not defined (bypassed)
            pass
        
        return response
    
    def _get_limit_type(self, request: Request) -> str:
        """Determine rate limit type based on request path"""
        path = request.url.path
        
        if path.startswith("/api/v1/auth"):
            return "auth"
        elif path.startswith("/api/v1/processing/upload") or path.startswith("/api/v1/ocr/extract"):
            return "upload"
        elif path.startswith("/api/v1"):
            return "per_user"
        else:
            return "per_ip"
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from request state (if authenticated)
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

class DistributedRateLimiter:
    """Distributed rate limiter for multi-instance deployments"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.rate_limiter = AdvancedRateLimiter(redis_client)
    
    async def check_distributed_limit(
        self,
        key: str,
        limit_type: str = "per_ip",
        custom_limits: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Check distributed rate limit across multiple instances"""
        # Use Redis Lua script for atomic operations
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        -- Remove expired entries
        redis.call('ZREMRANGEBYSCORE', key, 0, current_time - window)
        
        -- Count current requests
        local current_count = redis.call('ZCARD', key)
        
        if current_count >= limit then
            return {0, 0, 0, 0}
        end
        
        -- Add current request
        redis.call('ZADD', key, current_time, current_time)
        redis.call('EXPIRE', key, window)
        
        return {1, current_count + 1, limit - current_count - 1, current_time + window}
        """
        
        limits = custom_limits or self.rate_limiter.default_limits.get(limit_type, self.rate_limiter.default_limits["per_ip"])
        current_time = int(time.time())
        
        result = await self.redis.eval(
            lua_script,
            1,
            f"distributed_rate_limit:{limit_type}:{key}",
            limits["requests"],
            limits["window"],
            current_time
        )
        
        allowed, current_count, remaining, reset_time = result
        
        if not allowed:
            raise RateLimitExceeded(
                detail=f"Distributed rate limit exceeded. {limits['requests']} requests per {limits['window']} seconds allowed.",
                retry_after=reset_time - current_time
            )
        
        return {
            "limit": limits["requests"],
            "remaining": remaining,
            "reset_time": reset_time,
            "retry_after": 0
        }
