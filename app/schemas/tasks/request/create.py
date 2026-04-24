from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=20)
    description: str = Field(..., min_length=1, max_length=200)
    user_id: UUID
