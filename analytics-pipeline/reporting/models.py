"""
Pydantic models for reporting API responses.
"""
from datetime import date

from pydantic import BaseModel


class DailyAggregateResponse(BaseModel):
    """
    Schema for the response representing daily aggregates.
    """
    store_id: str
    date: date
    unique_users: int
    sessions: int
    page_views: int
    add_to_cart: int
    checkout_start: int
    checkout_success: int


class JourneyResponse(BaseModel):
    """
    Schema for user journey response.
    """
    checkout_id: str
    user_identity_id: str
    events: list[dict]
