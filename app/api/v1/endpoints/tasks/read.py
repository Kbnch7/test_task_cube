from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.tasks.tasks_router import tasks_router
from app.database.session import get_db
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
    session: AsyncSession = Depends(get_db)
) -> TaskResponseList:
    try:
        pagination_schema = Pagination(skip=skip, limit=limit)
        users = await tasks_service.read_all(session, pagination_schema)
        return users
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
    session: AsyncSession = Depends(get_db)
) -> TaskResponse:
    try:
        id_schema = TaskGet(id=id)
        users = await tasks_service.read(session, id_schema)
        return users
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
