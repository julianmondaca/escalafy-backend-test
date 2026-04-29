"""
API endpoints for serving aggregated data and reports.
"""
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from .queries import fetch_daily_aggregates, fetch_journey
from .models import DailyAggregateResponse, JourneyResponse

router = APIRouter()


@router.get("/stores/{store_id}/report")
async def get_daily_report(
    store_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...)
) -> dict:
    """
    Returns daily aggregated metrics for a specific store and date range.
    """
    try:
        aggregates = await fetch_daily_aggregates(store_id, start_date, end_date)
        return {
            "store_id": store_id,
            "start_date": start_date,
            "end_date": end_date,
            "data": [DailyAggregateResponse(**agg) for agg in aggregates]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversions/{checkout_id}/journey")
async def get_conversion_journey(checkout_id: str) -> JourneyResponse:
    """
    Returns the complete user journey for a specific checkout.
    """
    try:
        journey = await fetch_journey(checkout_id)
        if not journey:
            raise HTTPException(status_code=404, detail="Journey not found")
        return journey
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
