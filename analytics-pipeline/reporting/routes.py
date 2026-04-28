"""
API endpoints for serving aggregated data and reports.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/reports/daily")
async def get_daily_report() -> dict:
    """
    Returns daily aggregated metrics for a specific store.
    """
    # TODO: Implement query delegation and response shaping
    pass
