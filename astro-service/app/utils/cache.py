# ============================================
# astro-service/app/utils/cache.py
# ============================================
"""
Caching utilities for predictions and TLE data.
Supports Redis and in-memory fallback.
"""

import json
import hashlib
import pickle
from typing import Any, Optional, Callable, Dict
from datetime import datetime, timedelta
from functools import wraps
import logging
import redis.asyncio as redis
from asyncio import Lock

logger = logging.getLogger(__name__)


# ============================================
# Cache Key Generator
# ============================================

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key from arguments.
    
    Args:
        prefix: Cache key prefix (e.g., 'prediction', 'tle', 'passes')
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
    
    Returns:
        Hashed cache key string
    
    Examples:
        >>> generate_cache_key('prediction', 'ISS', 40.7, -74.0)
        'prediction:a1b2c3d4e5f6'
        
        >>> generate_cache_key('passes', satellite='ISS', lat=40.7, lng=-74.0)
        'passes:x1y2z3'
    """
    # Combine all arguments into a string
    parts = [str(arg) for arg in args]
    parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    # Create hash
    content = ":".join(parts)
    hash_obj = hashlib.md5(content.encode())
    hash_str = hash_obj.hexdigest()[:12]  # Use first 12 chars
    
    return f"{prefix}:{hash_str}"


def generate_prediction_key(
    satellite_name: str,
    lat: float,
    lng: float,
    timestamp: datetime,
    cloud_cover: float = 0,
    light_pollution: float = 0.5
) -> str:
    """Generate cache key for prediction."""
    # Round coordinates and timestamp for better cache hits
    lat_rounded = round(lat, 3)
    lng_rounded = round(lng, 3)
    time_rounded = timestamp.replace(second=0, microsecond=0)
    
    return generate_cache_key(
        'prediction',
        satellite_name.upper(),
        lat_rounded,
        lng_rounded,
        time_rounded.isoformat(),
        int(cloud_cover),
        int(light_pollution * 10)
    )


def generate_tle_key(satellite_name: str, source: str) -> str:
    """Generate cache key for TLE data."""
    return f"tle:{source}:{satellite_name.upper()}"


def generate_passes_key(
    satellite_name: str,
    lat: float,
    lng: float,
    days_ahead: int
) -> str:
    """Generate cache key for passes."""
    lat_rounded = round(lat, 2)
    lng_rounded = round(lng, 2)
    
    return generate_cache_key(
        'passes',
        satellite_name.upper(),
        lat_rounded,
        lng_rounded,
        days_ahead
    )


# ============================================
# Redis Cache Manager
# ============================================

class RedisCache:
    """Redis-based caching with automatic serialization."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,
        key_prefix: str = "singularity"
    ):
        """
        Initialize Redis cache.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
            key_prefix: Prefix for all cache keys
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self):
        """Connect to Redis."""
        if self._connected:
            return
        
        try:
            self.client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            await self.client.ping()
            self._connected = True
            logger.info(f"✓ Redis connected: {self.redis_url}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            self.client = None
            self._connected = False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("Redis disconnected")
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.key_prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        if not self.client:
            return None
        
        try:
            full_key = self._make_key(key)
            value = await self.client.get(full_key)
            
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                logger.debug(f"Cache MISS: {key}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Cache deserialization error for {key}: {e}")
            # Delete corrupted cache entry
            await self.delete(key)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (None = use default)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.default_ttl
            
            # Serialize value
            serialized = json.dumps(value, default=str)
            
            # Set with expiration
            await self.client.setex(full_key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
            
        except (TypeError, ValueError) as e:
            logger.error(f"Cache serialization error for {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False
        
        try:
            full_key = self._make_key(key)
            await self.client.delete(full_key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.client:
            return False
        
        try:
            full_key = self._make_key(key)
            return await self.client.exists(full_key) > 0
        except Exception as e:
            logger.error(f"Cache exists check error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., 'prediction:*')
        
        Returns:
            Number of keys deleted
        """
        if not self.client:
            return 0
        
        try:
            full_pattern = self._make_key(pattern)
            keys = []
            async for key in self.client.scan_iter(match=full_pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.client:
            return {
                "connected": False,
                "error": "Redis not connected"
            }
        
        try:
            info = await self.client.info()
            
            return {
                "connected": True,
                "total_keys": info.get("db0", {}).get("keys", 0),
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"connected": False, "error": str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# ============================================
# In-Memory Cache (Fallback)
# ============================================

class InMemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize in-memory cache."""
        self.default_ttl = default_ttl
        self._cache: Dict[str, tuple] = {}  # {key: (value, expiry_time)}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                
                # Check if expired
                if datetime.now() > expiry:
                    del self._cache[key]
                    self._misses += 1
                    logger.debug(f"Cache EXPIRED: {key}")
                    return None
                
                self._hits += 1
                logger.debug(f"Cache HIT (memory): {key}")
                return value
            else:
                self._misses += 1
                logger.debug(f"Cache MISS (memory): {key}")
                return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expiry = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = (value, expiry)
            logger.debug(f"Cache SET (memory): {key} (TTL: {ttl}s)")
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache DELETE (memory): {key}")
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.get(key) is not None
    
    async def clear(self):
        """Clear all cache."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared {count} entries from memory cache")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0.0
            
            return {
                "type": "in_memory",
                "total_keys": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2)
            }


# ============================================
# Cache Decorator
# ============================================

def cached(
    ttl: int = 3600,
    key_func: Optional[Callable] = None
):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Cache TTL in seconds
        key_func: Function to generate cache key from args
    
    Example:
        @cached(ttl=3600, key_func=lambda sat, lat, lng: f"{sat}:{lat}:{lng}")
        async def predict_visibility(satellite, lat, lng):
            # expensive calculation
            return result
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache instance from first arg (usually self)
            cache = kwargs.get('cache')
            if cache is None and args and hasattr(args[0], 'cache'):
                cache = args[0].cache
            
            if cache is None:
                # No cache available, execute function
                return await func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                cache_key = generate_cache_key(
                    func.__name__,
                    *args[1:],  # Skip self
                    **kwargs
                )
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator
