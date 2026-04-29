"""
Redis client for pushing events to the queue.
"""
import json

import redis.asyncio as redis

from config import settings

QUEUE_NAME = "events_queue"


class QueueClient:
    """
    Handles connection and communication with the Redis queue.
    """
    def __init__(self) -> None:
        self.redis = redis.from_url(settings.redis_url)

    async def push_event(self, event_data: dict) -> None:
        """
        Pushes a single event object to the Redis queue.
        """
        event_json = json.dumps(event_data)
        await self.redis.rpush(QUEUE_NAME, event_json)
