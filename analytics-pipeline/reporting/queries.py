"""
SQL queries to fetch analytical data from PostgreSQL.
"""
from datetime import datetime, date

from db.connection import get_pool


async def fetch_daily_aggregates(store_id: str, start_date: date, end_date: date) -> list[dict]:
    """
    Executes a query to retrieve daily aggregates for a given store and date range.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                store_id, date, unique_users, sessions,
                page_views, add_to_cart, checkout_start, checkout_success
            FROM daily_store_aggregates
            WHERE store_id = $1 AND date BETWEEN $2 AND $3
            ORDER BY date DESC
        """, store_id, start_date, end_date)
        return [dict(row) for row in rows]


async def calculate_daily_aggregates(store_id: str, target_date: date) -> None:
    """
    Calculates and upserts daily aggregates for a store on a specific date.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        # Get counts from events table
        day_start = f"{target_date}T00:00:00Z"
        day_end = f"{target_date}T23:59:59Z"

        aggs = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT s.user_identity_id) as unique_users,
                COUNT(DISTINCT e.session_id) as sessions,
                SUM(CASE WHEN e.event_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
                SUM(CASE WHEN e.event_type = 'add_to_cart' THEN 1 ELSE 0 END) as add_to_cart,
                SUM(CASE WHEN e.event_type = 'checkout_start' THEN 1 ELSE 0 END) as checkout_start,
                SUM(CASE WHEN e.event_type = 'checkout_success' THEN 1 ELSE 0 END) as checkout_success
            FROM events e
            LEFT JOIN sessions s ON e.session_id = s.session_id
            WHERE e.store_id = $1 AND DATE(e.timestamp) = $2
        """, store_id, target_date)

        await conn.execute("""
            INSERT INTO daily_store_aggregates (store_id, date, unique_users, sessions, page_views, add_to_cart, checkout_start, checkout_success)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (store_id, date) DO UPDATE SET
                unique_users = EXCLUDED.unique_users,
                sessions = EXCLUDED.sessions,
                page_views = EXCLUDED.page_views,
                add_to_cart = EXCLUDED.add_to_cart,
                checkout_start = EXCLUDED.checkout_start,
                checkout_success = EXCLUDED.checkout_success,
                updated_at = NOW()
        """, store_id, target_date,
            aggs['unique_users'] or 0, aggs['sessions'] or 0,
            aggs['page_views'] or 0, aggs['add_to_cart'] or 0,
            aggs['checkout_start'] or 0, aggs['checkout_success'] or 0)


async def fetch_journey(checkout_id: str) -> dict:
    """
    Fetches the complete journey for a given checkout.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        # Get user_identity_id from checkout event
        checkout_event = await conn.fetchrow("""
            SELECT s.user_identity_id, e.session_id
            FROM events e
            LEFT JOIN sessions s ON e.session_id = s.session_id
            WHERE e.event_type = 'checkout_success' AND e.event_object_id = $1
            LIMIT 1
        """, checkout_id)

        if not checkout_event:
            return None

        user_identity_id = checkout_event['user_identity_id']

        # Get all events for this user identity
        events = await conn.fetch("""
            SELECT e.event_type, e.timestamp, e.event_object_id, e.store_id
            FROM events e
            LEFT JOIN sessions s ON e.session_id = s.session_id
            WHERE s.user_identity_id = $1
            ORDER BY e.timestamp ASC
        """, user_identity_id)

        return {
            "checkout_id": checkout_id,
            "user_identity_id": str(user_identity_id),
            "events": [dict(e) for e in events]
        }
