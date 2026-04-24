from fastapi import Depends, HTTPException, status
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import CACHE_TTL
from app.data.redis.redis_session import get_redis
from app.data.redis.utils import set_object_to_redis
from app.data.session import get_db
from app.schemas.tasks.request import TaskCreate
from app.schemas.tasks.response import TaskResponse
from app.services.tasks_service import tasks_service
from app.services.utils.exceptions import (
    DatabaseError,
)

from .tasks_router import tasks_router


@tasks_router.post(
    '/',
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_task_handler(
    task_data: TaskCreate,
    db_session: AsyncSession = Depends(get_db),
    redis_session: Redis = Depends(get_redis)
):
    try:
        task = await tasks_service.create(db_session, task_data)
        await set_object_to_redis(
            redis_session, str(task.id), TaskResponse.model_validate(task), CACHE_TTL
        )
        return task
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        ) from e
