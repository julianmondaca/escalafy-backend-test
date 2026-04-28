"""
Domain models for user identity and sessions.
"""
from dataclasses import dataclass

@dataclass
class UserIdentity:
    """
    Represents a unique user identity across sessions.
    """
    id: str
    store_id: str
    created_at: str

@dataclass
class Session:
    """
    Represents a period of user activity.
    """
    id: str
    session_id: str
    user_identity_id: str
    store_id: str
    first_seen: str
    last_seen: str
