"""
Handles user identity resolution and session management.
"""
import asyncio
import logging
from uuid import uuid4

from db.connection import get_pool

logger = logging.getLogger(__name__)


class IdentityWorker:
    """
    Processes events to resolve and link user identities.
    """

    async def link_identities(self) -> None:
        """
        Periodically processes unlinked events to resolve user identities.
        Links sessions by user_ip and checkout_id.
        """
        pool = get_pool()
        while True:
            try:
                async with pool.acquire() as conn:
                    # Get unlinked sessions
                    unlinked_sessions = await conn.fetch("""
                        SELECT DISTINCT e.session_id, e.store_id, e.user_ip
                        FROM events e
                        LEFT JOIN sessions s ON e.session_id = s.session_id AND e.store_id = s.store_id
                        WHERE s.id IS NULL
                        LIMIT 100
                    """)

                    for session in unlinked_sessions:
                        session_id = session['session_id']
                        store_id = session['store_id']
                        user_ip = session['user_ip']

                        # Check if user_identity exists for this IP
                        identity = await conn.fetchrow("""
                            SELECT id FROM user_identities WHERE user_ip = $1
                        """, user_ip)

                        if identity is None:
                            # Create new user_identity
                            identity_id = str(uuid4())
                            await conn.execute("""
                                INSERT INTO user_identities (id, user_ip)
                                VALUES ($1, $2)
                                ON CONFLICT (user_ip) DO NOTHING
                            """, identity_id, user_ip)
                        else:
                            identity_id = identity['id']

                        # Link session to identity
                        await conn.execute("""
                            INSERT INTO sessions (user_identity_id, session_id, store_id)
                            VALUES ($1, $2, $3)
                            ON CONFLICT (session_id, store_id) DO NOTHING
                        """, identity_id, session_id, store_id)

                    logger.info(f"Linked {len(unlinked_sessions)} sessions to user identities")

            except Exception as e:
                logger.error(f"Error in identity linking: {e}", exc_info=True)

            await asyncio.sleep(10)  # Run every 10 seconds


async def resolve_identity(session_id: str, store_id: str) -> str:
    """
    Resolves a session ID to a known or new user identity.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        session = await conn.fetchrow("""
            SELECT user_identity_id FROM sessions
            WHERE session_id = $1 AND store_id = $2
        """, session_id, store_id)

        if session:
            return session['user_identity_id']
        return None


async def run_identity_worker() -> None:
    """
    Start the identity worker process.
    """
    logger.info("Identity worker started")
    worker = IdentityWorker()
    try:
        await worker.link_identities()
    except KeyboardInterrupt:
        logger.info("Identity worker shutting down")


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    asyncio.run(run_identity_worker())
