from uuid import UUID

from pydantic import BaseModel, Field


class TaskUpdate(BaseModel):
    id: UUID | None = None
    status: str = Field(..., min_length=1, max_length=20)
