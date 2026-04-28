"""
API endpoints for event ingestion.
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/events")
async def ingest_event() -> dict[str, str]:
    """
    Receives an event, validates it, and pushes it to the queue.
    """
    # TODO: Implement event validation and queueing logic
    pass
