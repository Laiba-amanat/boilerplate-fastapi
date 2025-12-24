import json
from collections.abc import Callable
from functools import wraps
from typing import Any

import redis.asyncio as redis

from log import logger
from schemas.base import Fail, Success, SuccessExtra
from settings.config import settings


class CacheManager:
    """Redis cache manager"""

    def __init__(self):
        self.redis: redis.Redis | None = None
        self._connection_pool = None

    async def connect(self):
        """Connect to Redis"""
        if self.redis is None:
            try:
                self.redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    retry_on_timeout=True,
                )
                # Test connection
                await self.redis.ping()
                logger.info("Redis connection successful")
            except Exception as e:
                logger.warning(f"Redis connection failed: {str(e)}, cache functionality will be disabled")
                self.redis = None

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("Redis connection disconnected")

    async def get(self, key: str) -> Any | None:
        """Get cache value"""
        if not self.redis:
            return None

        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache key={key}: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set cache value"""
        if not self.redis:
            return False

        try:
            ttl = ttl or settings.CACHE_TTL
            serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            await self.redis.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache key={key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete cache"""
        if not self.redis:
            return False

        try:
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete cache key={key}: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False

        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to check cache existence key={key}: {str(e)}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache by pattern"""
        if not self.redis:
            return 0

        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to batch delete cache pattern={pattern}: {str(e)}")
            return 0

    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key"""
        key_parts = [prefix]

        # Add positional arguments
        if args:
            key_parts.extend(str(arg) for arg in args)

        # Add keyword arguments
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend(f"{k}:{v}" for k, v in sorted_kwargs)

        return ":".join(key_parts)


# Global cache manager instance
cache_manager = CacheManager()


def cached(prefix: str, ttl: int | None = None, key_func: Callable | None = None):
    """Cache decorator

    Args:
        prefix: Cache key prefix
        ttl: Expiration time (seconds)
        key_func: Custom key generation function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_manager.cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                if isinstance(cached_result, dict) and cached_result.get("__response__"):
                    response_type = cached_result.get("class")
                    payload = cached_result.get("payload", {})
                    response_cls = {
                        "Success": Success,
                        "Fail": Fail,
                        "SuccessExtra": SuccessExtra,
                    }.get(response_type, Success)
                    return response_cls(**payload)
                return cached_result

            # Execute original function
            result = await func(*args, **kwargs)

            # Set cache
            if result is not None:
                value_to_cache: Any = result
                if isinstance(result, (Success, Fail, SuccessExtra)):
                    body_bytes = result.body
                    if isinstance(body_bytes, bytes):
                        payload = json.loads(body_bytes.decode("utf-8"))
                    else:
                        payload = json.loads(body_bytes)
                    value_to_cache = {
                        "__response__": True,
                        "class": result.__class__.__name__,
                        "payload": payload,
                    }
                await cache_manager.set(cache_key, value_to_cache, ttl)
                logger.debug(f"Cache set: {cache_key}")

            return result

        return wrapper

    return decorator


# Cache cleanup utility functions
async def clear_user_cache(user_id: int):
    """Clear user-related cache"""
    patterns = [
        f"user:{user_id}:*",
        f"userinfo:{user_id}",
        f"user_roles:{user_id}",
        f"user_permissions:{user_id}",
    ]

    total_cleared = 0
    for pattern in patterns:
        cleared = await cache_manager.clear_pattern(pattern)
        total_cleared += cleared

    logger.info(f"Cleared user {user_id} related cache, total {total_cleared} keys")
    return total_cleared


async def clear_role_cache(role_id: int):
    """Clear role-related cache"""
    patterns = [
        f"role:{role_id}:*",
        f"role_permissions:{role_id}",
        f"role_menus:{role_id}",
    ]

    total_cleared = 0
    for pattern in patterns:
        cleared = await cache_manager.clear_pattern(pattern)
        total_cleared += cleared

    logger.info(f"Cleared role {role_id} related cache, total {total_cleared} keys")
    return total_cleared
