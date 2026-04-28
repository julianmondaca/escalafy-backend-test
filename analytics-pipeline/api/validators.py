"""
Pydantic validators for incoming API requests.
"""
from pydantic import BaseModel

class EventPayload(BaseModel):
    """
    Schema for incoming event payload.
    """
    # TODO: Define validation fields matching the event structure
    pass
