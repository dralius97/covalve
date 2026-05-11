import redis.asyncio as redis
from typing import Any

_client = None

async def get_redis():
    global _client
    if _client is None:
        _client = redis.from_url("redis://localhost:6379")
    return _client

async def redis_set(key: str, value: Any) -> None:
    client = await get_redis()
    await client.set(key, value)


async def redis_get(key: str) -> str | None:
    client = await get_redis()
    return await client.get(key)


async def redis_delete(key: str) -> None:
    client = await get_redis()
    await client.delete(key)

