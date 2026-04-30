"""
Main worker process that polls the queue and orchestrates processing.
"""
import asyncio
import json
import logging

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from config import settings
from db.connection import init_pool, close_pool
from workers.batch_writer import BatchWriter
from workers.deduplication import DeduplicationCache

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

STREAM_NAME = "events_stream"
CONSUMER_GROUP = "consumer_group"
CONSUMER_NAME = "consumer_1"


async def run_worker() -> None:
    """
    Starts the consumer loop, pulling events from Redis and processing them.
    """
    await init_pool()
    redis_client = Redis.from_url(settings.redis_url)
    batch_writer = BatchWriter()
    dedup_cache = DeduplicationCache(redis_client)

    try:
        await redis_client.xgroup_create(STREAM_NAME, CONSUMER_GROUP, id="0", mkstream=True)
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

    try:
        while True:
            # Read from Redis Stream
            events = await redis_client.xreadgroup(
                CONSUMER_GROUP, CONSUMER_NAME, {STREAM_NAME: ">"}, count=10, block=5000
            )
            if not events:
                continue

            for stream_event in events:
                _, event_data = stream_event
                if not event_data:
                    continue

                for message_id, message_dict in event_data:
                    event_json = message_dict.get(b"data") or message_dict.get("data")
                    if isinstance(event_json, bytes):
                        event_json = event_json.decode('utf-8')

                    try:
                        event_obj = json.loads(event_json)
                        logger.info(f"Processing event: {event_obj}")
                        # Check deduplication
                        event_id_str = f"{event_obj['store_id']}:{event_obj['session_id']}:{event_obj['timestamp']}:{event_obj['event_object_id']}"
                        if await dedup_cache.is_duplicate(event_id_str):
                            logger.info(f"Skipping duplicate event: {event_id_str}")
                            await redis_client.xack(STREAM_NAME, CONSUMER_GROUP, message_id)
                            continue

                        # Insert event
                        logger.info(f"Inserting event to database: {event_id_str}")
                        await batch_writer.insert_event(event_obj)
                        await dedup_cache.mark_processed(event_id_str)
                        logger.info(f"Event inserted successfully: {event_id_str}")

                        # Acknowledge the event after processing
                        await redis_client.xack(STREAM_NAME, CONSUMER_GROUP, message_id)

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in stream: {event_json}, error: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing event: {e}", exc_info=True)
                        # Poison pill: skip and continue
                        continue

    except KeyboardInterrupt:
        pass
    finally:
        await close_pool()
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
