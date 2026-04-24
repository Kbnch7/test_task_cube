from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
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
    session: AsyncSession = Depends(get_db)
):
    try:
        task = await tasks_service.create(session, task_data)
        return task
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        ) from e
