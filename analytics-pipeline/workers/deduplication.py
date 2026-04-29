"""
Deduplication logic to prevent processing exactly same events twice.
"""
import redis.asyncio as redis


class DeduplicationCache:
    """
    Cache for deduplication using Redis.
    """

    def __init__(self, redis_client: redis.Redis, ttl_seconds: int = 3600):
        self.redis = redis_client
        self.ttl = ttl_seconds

    async def is_duplicate(self, event_id: str) -> bool:
        """
        Checks if an event with the given ID has already been recently processed.
        """
        key = f"processed:{event_id}"
        exists = await self.redis.exists(key)
        return exists > 0

    async def mark_processed(self, event_id: str) -> None:
        """
        Marks an event as processed.
        """
        key = f"processed:{event_id}"
        await self.redis.setex(key, self.ttl, "1")


async def is_duplicate(event_id: str) -> bool:
    """
    Checks if an event with the given ID has already been recently processed.
    """
    # Legacy function, use DeduplicationCache instead
    return False
