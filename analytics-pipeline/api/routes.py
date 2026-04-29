"""
API endpoints for event ingestion.
"""
from fastapi import APIRouter, HTTPException, status

from .queue_client import QueueClient
from .validators import BatchEventPayload, EventPayload

router = APIRouter()
queue_client = QueueClient()


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(event: EventPayload) -> dict[str, str]:
    """
    Receives an event, validates it, and pushes it to the queue.
    """
    try:
        await queue_client.push_event(event.model_dump())
        return {"message": "Event accepted"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/events/batch", status_code=status.HTTP_202_ACCEPTED)
async def ingest_batch_events(batch: BatchEventPayload) -> dict[str, str]:
    """
    Receives a batch of events, validates them, and pushes them to the queue.
    """
    try:
        for event in batch.events:
            await queue_client.push_event(event.model_dump())
        return {"message": f"Batch of {len(batch.events)} events accepted"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
