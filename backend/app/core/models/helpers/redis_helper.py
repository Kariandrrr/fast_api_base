from typing import AsyncGenerator

from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings


class RedisHelper:
    def __init__(self, url: str) -> None:
        self.pool = ConnectionPool.from_url(url=url)

    def get_client(self) -> Redis:
        return Redis(connection_pool=self.pool, decode_responses=True)

    async def dispose(self) -> None:
        await self.pool.aclose()

    async def client_getter(self) -> AsyncGenerator[Redis, None]:
        async with self.get_client() as client:
            yield client


redis_helper = RedisHelper(url=str(settings.db.redis.url))
