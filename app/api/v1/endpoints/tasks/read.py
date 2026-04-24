from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.tasks.tasks_router import tasks_router
from app.config import CACHE_TTL, CACHE_TTL_TASKS
from app.data.redis.redis_session import get_redis
from app.data.redis.utils import get_object_from_redis, set_object_to_redis
from app.data.session import get_db
from app.schemas.tasks.request import Pagination, TaskGet
from app.schemas.tasks.response import TaskResponse, TaskResponseList
from app.services.tasks_service import tasks_service
from app.services.utils.exceptions import DatabaseError, TaskNotFoundError


@tasks_router.get(
    '/',
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK
)
async def get_tasks_handler(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db_session: AsyncSession = Depends(get_db),
    redis_session: Redis = Depends(get_redis)
) -> TaskResponseList:
    try:
        pagination_schema = Pagination(skip=skip, limit=limit)
        key = f"tasks:pagination:{skip}:{limit}"
        cached_data = await get_object_from_redis(redis_session, key, TaskResponseList)
        if cached_data:
            return cached_data.tasks
        tasks_db = await tasks_service.read_all(db_session, pagination_schema)
        tasks_schemas = [TaskResponse.model_validate(task) for task in tasks_db]
        tasks_list_container = TaskResponseList(tasks=tasks_schemas)
        await set_object_to_redis(
            redis_session, key, tasks_list_container, CACHE_TTL_TASKS
        )
        return tasks_schemas
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        ) from e

@tasks_router.get(
    '/{id}',
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK
)
async def get_task_handler(
    id: UUID,
    db_session: AsyncSession = Depends(get_db),
    redis_session: Redis = Depends(get_redis)
) -> TaskResponse:
    try:
        id_schema = TaskGet(id=id)
        task = await get_object_from_redis(redis_session, str(id), TaskResponse)
        if task:
            return task
        task = await tasks_service.read(db_session, id_schema)
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
