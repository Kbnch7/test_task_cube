from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Task
from app.schemas.tasks.request import (
    Pagination,
    TaskCreate,
    TaskDelete,
    TaskGet,
    TaskUpdate,
)


class TasksRepository:
    async def create(self, session: AsyncSession, task_data: TaskCreate) -> Task:
        async with session.begin():
            task = Task(**task_data.model_dump())
            session.add(task)
            await session.flush()
            await session.refresh(task)
            return task

    async def read_all(
        self, session: AsyncSession, pagination: Pagination
    ) -> list[Task]:
        result = await session.execute(
            select(Task)
            .offset(pagination.skip)
            .limit(pagination.limit)
        )
        tasks = result.scalars().all()
        return tasks

    async def read(self, session: AsyncSession, task_data: TaskGet) -> Task|None:
        result = await session.execute(
            select(Task).where(Task.id == task_data.id)
        )
        task = result.scalar_one_or_none()
        return task

    async def update(self, session: AsyncSession, task_data: TaskUpdate) -> Task|None:
        async with session.begin():
            result = await session.execute(
                select(Task).where(Task.id == task_data.id)
            )
            task = result.scalar_one_or_none()
            if task:
                task.status = task_data.status
            return task

    async def delete(self, session: AsyncSession, task_data: TaskDelete) -> Task|None:
        async with session.begin():
            result = await session.execute(
                select(Task).where(Task.id == task_data.id)
            )
            task = result.scalar_one_or_none()
            if task:
                session.delete(task)
            return task

tasks_repository = TasksRepository()
