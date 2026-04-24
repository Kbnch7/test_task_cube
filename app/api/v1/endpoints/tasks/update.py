from uuid import UUID

from fastapi import Depends, HTTPException, status
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.tasks.tasks_router import tasks_router
from app.config import CACHE_TTL
from app.data.redis.redis_session import get_redis
from app.data.redis.utils import delete_object_from_redis, set_object_to_redis
from app.data.session import get_db
from app.schemas.tasks.request import TaskUpdate
from app.schemas.tasks.response import TaskResponse
from app.services.tasks_service import tasks_service
from app.services.utils.exceptions import (
    DatabaseError,
    TaskAlreadyDoneError,
    TaskNotFoundError,
)


@tasks_router.patch(
    '/{id}',
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK
)
async def update_task_handler(
    id: UUID,
    task_data: TaskUpdate,
    db_session: AsyncSession = Depends(get_db),
    redis_session: Redis = Depends(get_redis)
):
    try:
        task_data.id = id
        task = await tasks_service.update(db_session, task_data)
        await delete_object_from_redis(redis_session, str(id))
        await set_object_to_redis(
            redis_session, str(id), TaskResponse.model_validate(task), CACHE_TTL
        )
        return task
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        ) from e
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        ) from e
    except TaskAlreadyDoneError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already done"
        ) from e
