import redis.asyncio as redis
from jotsu.mcp.server import AsyncCache

from app import settings


class RedisCache(AsyncCache):

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expires_in: int | None = None):
        return await self.redis.set(key, value, ex=expires_in)

    async def delete(self, key: str):
        return await self.redis.delete(key)
