import asyncpg
from core.config import settings


class DBConnect:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.db_url)
        return self.pool

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, params: tuple = ()) -> tuple:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *params)

    async def fetchall(self, query: str, params: tuple = ()) -> list:
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *params)

    async def fetchone(self, query: str, params: tuple = ()) -> tuple:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *params)


db = DBConnect(settings.DATABASE_URL)
