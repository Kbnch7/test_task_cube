from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Task
from app.database.repositories import TasksRepository
from app.database.repositories.tasks import tasks_repository
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


class TasksService:
    def __init__(self, tasks_repository: TasksRepository):
        self.tasks_repository = tasks_repository

    @catch_sqlalchemy_errors
    async def create(self, session: AsyncSession, task_data: TaskCreate) -> Task:
        task = await self.tasks_repository.create(session, task_data)
        await session.commit()
        return task

    @catch_sqlalchemy_errors
    async def read_all(
        self, session: AsyncSession, tasks_pagination: Pagination
    ) -> list[Task]:
        tasks = await self.tasks_repository.read_all(session, tasks_pagination)
        await session.commit()
        return tasks

    @catch_sqlalchemy_errors
    @catch_task_not_found_error
    async def read(self, session: AsyncSession, task_data: TaskGet) -> Task:
        task = await self.tasks_repository.read(session,task_data)
        return task

    @catch_sqlalchemy_errors
    @catch_task_not_found_error
    async def update(self, session: AsyncSession, task_data: TaskUpdate) -> Task:
        async with session.begin():
            task = await self.tasks_repository.update(session, task_data)
        return task

    @catch_sqlalchemy_errors
    @catch_task_not_found_error
    async def delete(self, session: AsyncSession, task_data: TaskDelete):
        async with session.begin():
            task = await self.tasks_repository.delete(session, task_data)
        return task

tasks_service = TasksService(tasks_repository)
