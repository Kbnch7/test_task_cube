from uuid import UUID

from pydantic import BaseModel


class TaskResponse(BaseModel):
    id: UUID
    title: str
    status: str
    description: str
    user_id: UUID
    created_at: str
    updated_at: str

class TaskResponseList(BaseModel):
    tasks: list[TaskResponse]
