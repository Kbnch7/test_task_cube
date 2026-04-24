from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.config import REDIS_URL

redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

async def get_redis() -> AsyncGenerator[redis.Redis]:
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()
