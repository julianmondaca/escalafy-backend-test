"""
Main worker process that polls the queue and orchestrates processing.
"""
import asyncio
import json
import logging

import redis.asyncio as redis

from config import settings
from db.connection import init_pool, close_pool
from workers.batch_writer import BatchWriter
from workers.deduplication import DeduplicationCache

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

QUEUE_NAME = "events_queue"


async def run_worker() -> None:
    """
    Starts the consumer loop, pulling events from Redis and processing them.
    """
    logger.info("Initializing worker...")
    await init_pool()
    redis_client = redis.from_url(settings.redis_url)
    batch_writer = BatchWriter()
    dedup_cache = DeduplicationCache(redis_client)

    try:
        logger.info("Worker started, polling for events...")
        while True:
            # Poll for events
            raw_event = await redis_client.blpop(QUEUE_NAME, timeout=1)
            if raw_event is None:
                continue

            _, event_json = raw_event
            try:
                event = json.loads(event_json)
                logger.info(f"Processing event: {event}")
                # Check deduplication
                event_id = f"{event['store_id']}:{event['session_id']}:{event['timestamp']}:{event['event_object_id']}"
                if await dedup_cache.is_duplicate(event_id):
                    logger.info(f"Skipping duplicate event: {event_id}")
                    continue

                # Insert event
                logger.info(f"Inserting event to database: {event_id}")
                await batch_writer.insert_event(event)
                await dedup_cache.mark_processed(event_id)
                logger.info(f"Event inserted successfully: {event_id}")

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in queue: {event_json}, error: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)
                # Poison pill: skip and continue
                continue

    except KeyboardInterrupt:
        logger.info("Shutting down worker")
    finally:
        await close_pool()
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
