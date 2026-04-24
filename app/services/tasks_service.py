from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models import Task
from app.data.repositories import TasksRepository
from app.data.repositories.tasks import tasks_repository
from app.schemas.tasks.request import (
    Pagination,
    TaskCreate,
    TaskDelete,
    TaskGet,
    TaskUpdate,
)
from app.services.utils.decorators import (
    catch_sqlalchemy_errors,
    catch_task_not_found_error,
)
from app.services.utils.exceptions import TaskAlreadyDoneError


class TasksService:
    def __init__(self, tasks_repository: TasksRepository):
        self.tasks_repository = tasks_repository

    @catch_sqlalchemy_errors
    async def create(self, db_session: AsyncSession, task_data: TaskCreate) -> Task:
        task = await self.tasks_repository.create(db_session, task_data)
        await db_session.commit()
        return task

    @catch_sqlalchemy_errors
    async def read_all(
        self, db_session: AsyncSession, tasks_pagination: Pagination
    ) -> list[Task]:
        tasks = await self.tasks_repository.read_all(db_session, tasks_pagination)
        await db_session.commit()
        return tasks

    @catch_sqlalchemy_errors
    @catch_task_not_found_error
    async def read(self, db_session: AsyncSession, task_data: TaskGet) -> Task:
        task = await self.tasks_repository.read(db_session,task_data)
        return task

    @catch_sqlalchemy_errors
    @catch_task_not_found_error
    async def update(self, db_session: AsyncSession, task_data: TaskUpdate) -> Task:
        async with db_session.begin():
            task = await self.tasks_repository.read(
                db_session, TaskGet(id=task_data.id)
            )
            if task.status == 'done':
                raise TaskAlreadyDoneError()
            task = await self.tasks_repository.update(db_session, task_data)
        return task

    @catch_sqlalchemy_errors
    @catch_task_not_found_error
    async def delete(self, db_session: AsyncSession, task_data: TaskDelete):
        async with db_session.begin():
            task = await self.tasks_repository.delete(db_session, task_data)
        return task

tasks_service = TasksService(tasks_repository)
