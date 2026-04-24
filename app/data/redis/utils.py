
from pydantic import BaseModel
from redis import Redis


async def set_object_to_redis(redis: Redis, key: str, obj: BaseModel, ex: int = 3600):
    await redis.set(key, obj.model_dump_json(), ex=ex)

async def get_object_from_redis(redis: Redis, key: str, model: type[BaseModel]):
    data = await redis.get(key)
    return model.model_validate_json(data) if data else None

async def delete_object_from_redis(redis: Redis, key: str):
    await redis.delete(key)
