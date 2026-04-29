"""
Writes batches of processed events to PostgreSQL.
"""
from datetime import datetime

from db.connection import get_pool


class BatchWriter:
    """
    Handles batch writing of events to the database.
    """

    async def insert_event(self, event: dict) -> None:
        """
        Inserts a single event into the database.
        """
        pool = get_pool()
        async with pool.acquire() as conn:
            event_id = f"{event['store_id']}:{event['session_id']}:{event['timestamp']}:{event['event_object_id']}"
            # Parse timestamp string to datetime
            timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            await conn.execute("""
                INSERT INTO events (store_id, event_type, session_id, timestamp, user_ip, event_object_id, event_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (event_id) DO NOTHING
            """, event['store_id'], event['event_type'], event['session_id'], timestamp,
                 event['user_ip'], event['event_object_id'], event_id)


async def write_events_batch(events: list) -> None:
    """
    Takes a batch of processed events and writes them to the database.
    """
    writer = BatchWriter()
    for event in events:
        await writer.insert_event(event)
