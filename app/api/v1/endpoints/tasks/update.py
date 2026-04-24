from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.tasks.tasks_router import tasks_router
from app.database.session import get_db
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
    session: AsyncSession = Depends(get_db)
):
    try:
        task_data.id = id
        task = await tasks_service.update(session, task_data)
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
