"""
Manages the async PostgreSQL connection pool.
"""
import asyncpg

_pool: asyncpg.Pool | None = None

async def init_pool() -> None:
    """
    Initializes the connection pool using the database URL from settings.
    """
    # TODO: Initialize the asyncpg connection pool and store it in _pool
    pass

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
    # TODO: Close the pool if it exists
    pass
