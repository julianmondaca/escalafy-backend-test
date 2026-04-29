"""
Pydantic validators for incoming API requests.
"""
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, field_validator


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT_START = "checkout_start"
    CHECKOUT_SUCCESS = "checkout_success"


class EventPayload(BaseModel):
    """
    Schema for incoming event payload.
    """
    store_id: str
    event_type: EventType
    session_id: str
    timestamp: str
    user_ip: str
    event_object_id: str

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("timestamp must be in ISO 8601 format")
        return v


class BatchEventPayload(BaseModel):
    """
    Schema for batch event payload.
    """
    events: List[EventPayload]

    @field_validator("events")
    @classmethod
    def validate_batch_size(cls, v: List[EventPayload]) -> List[EventPayload]:
        if len(v) > 100:
            raise ValueError("batch cannot exceed 100 events")
        return v
