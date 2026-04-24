from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TaskUpdate(BaseModel):
    id: UUID | None = None
    status: str = Field(..., min_length=1, max_length=20)

    @field_validator('status')
    @classmethod
    def status_check(cls, status: str) -> str:
        if status not in ['todo', 'in_progress', 'review', 'done']:
            raise ValueError('Status must be one of todo, in_progress, review, done')
        return status
