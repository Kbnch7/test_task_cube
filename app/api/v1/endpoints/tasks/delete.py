from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.tasks.tasks_router import tasks_router
from app.database.session import get_db
from app.schemas.tasks.request import TaskDelete
from app.services.tasks_service import tasks_service
from app.services.utils.exceptions import DatabaseError, TaskNotFoundError


@tasks_router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task_handler(
    id: UUID,
    session: AsyncSession = Depends(get_db)
):
    try:
        task_data = TaskDelete(id=id)
        await tasks_service.delete(session, task_data)
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
