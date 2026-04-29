"""
Manages the async PostgreSQL connection pool.
"""
import asyncpg

from config import settings

_pool: asyncpg.Pool | None = None

async def init_pool() -> None:
    """
    Initializes the connection pool using the database URL from settings.
    """
    global _pool
    _pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=10)

def get_pool() -> asyncpg.Pool:
    """
    Returns the initialized connection pool. Raises Exception if not initialized.
    """
    global _pool
    if _pool is None:
        raise Exception("Database pool is not initialized")
    return _pool

async def close_pool() -> None:
    """
    Closes the connection pool gracefully.
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
