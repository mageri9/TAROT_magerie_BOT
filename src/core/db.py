import asyncpg
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config import settings


class DBConnect:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None

    async def connect(self):
        """Создать пул соединений с БД."""
        self.pool = await asyncpg.create_pool(self.db_url)
        return self.pool

    async def close(self):
        """Закрыть пул."""
        if self.pool:
            await self.pool.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.1, min=0.1, max=2),
        retry=retry_if_exception_type(
            (
                asyncpg.ConnectionFailureError,
                asyncpg.TooManyConnectionsError,
                asyncpg.DeadlockDetectedError,
                ConnectionError,
                TimeoutError,
                OSError,
            )
        ),
        reraise=True,
    )
    async def execute(self, query: str, params: tuple = ()) -> tuple:
        logger.warning("DB execute called")
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *params)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.1, min=0.1, max=2),
        retry=retry_if_exception_type(
            (
                asyncpg.ConnectionFailureError,
                asyncpg.TooManyConnectionsError,
                asyncpg.DeadlockDetectedError,
                ConnectionError,
                TimeoutError,
                OSError,
            )
        ),
        reraise=True,
    )
    async def fetchall(self, query: str, params: tuple = ()) -> list:
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *params)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.1, min=0.1, max=2),
        retry=retry_if_exception_type(
            (
                asyncpg.ConnectionFailureError,
                asyncpg.TooManyConnectionsError,
                asyncpg.DeadlockDetectedError,
                ConnectionError,
                TimeoutError,
                OSError,
            )
        ),
        reraise=True,
    )
    async def fetchone(self, query: str, params: tuple = ()) -> tuple:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *params)


db = DBConnect(settings.DATABASE_URL)
