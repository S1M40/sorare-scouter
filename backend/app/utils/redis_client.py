import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheClient:
    """Async Redis client wrapper with in-memory fallback for local development/resilience."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
        self._memory_cache: dict[str, tuple[Any, float]] = {}  # key -> (val, expire_at)
        self._connected = False

    async def connect(self) -> None:
        try:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,
            )
            await self._client.ping()
            self._connected = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self._connected = False
            self._client = None
            logger.warning(f"Redis not reachable at {self.redis_url}. Using in-memory cache fallback. Error: {e}")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def get(self, key: str) -> Optional[Any]:
        if self._connected and self._client:
            try:
                val = await self._client.get(key)
                if val is not None:
                    try:
                        return json.loads(val)
                    except (json.JSONDecodeError, TypeError):
                        return val
                return None
            except Exception as e:
                logger.warning(f"Redis get failed for {key}: {e}")

        # In-memory fallback
        import time
        item = self._memory_cache.get(key)
        if item:
            val, expire_at = item
            if expire_at > time.time():
                return val
            else:
                del self._memory_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        serialized = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        if self._connected and self._client:
            try:
                await self._client.set(key, serialized, ex=ttl)
                return True
            except Exception as e:
                logger.warning(f"Redis set failed for {key}: {e}")

        # In-memory fallback
        import time
        self._memory_cache[key] = (value, time.time() + ttl)
        return True

    async def delete(self, key: str) -> bool:
        if self._connected and self._client:
            try:
                await self._client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed for {key}: {e}")
        self._memory_cache.pop(key, None)
        return True

    async def delete_prefix(self, prefix: str) -> None:
        """Invalidate all keys matching a prefix."""
        if self._connected and self._client:
            try:
                keys = []
                async for key in self._client.scan_iter(match=f"{prefix}*"):
                    keys.append(key)
                if keys:
                    await self._client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis delete_prefix failed for {prefix}: {e}")

        # In-memory cleanup
        to_delete = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
        for k in to_delete:
            del self._memory_cache[k]

    async def acquire_lock(self, lock_key: str, ttl: int = 60) -> bool:
        """Acquire a distributed lock for sync jobs."""
        full_key = f"sync_lock:{lock_key}"
        if self._connected and self._client:
            try:
                acquired = await self._client.set(full_key, "locked", ex=ttl, nx=True)
                return bool(acquired)
            except Exception as e:
                logger.warning(f"Redis lock acquire failed for {lock_key}: {e}")

        # In-memory fallback lock
        import time
        now = time.time()
        item = self._memory_cache.get(full_key)
        if item and item[1] > now:
            return False
        self._memory_cache[full_key] = ("locked", now + ttl)
        return True

    async def release_lock(self, lock_key: str) -> None:
        """Release a distributed lock."""
        await self.delete(f"sync_lock:{lock_key}")


cache = CacheClient(settings.REDIS_URL)
