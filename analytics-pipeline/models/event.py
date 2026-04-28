"""
Domain model representing an analytics event.
"""
from dataclasses import dataclass, field
import uuid

@dataclass
class Event:
    """
    Represents an event tracked in the system.
    """
    store_id: str
    event_type: str
    session_id: str
    timestamp: str
    user_ip: str
    event_object_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
