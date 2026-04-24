from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskResponse(BaseModel):
    id: UUID
    title: str
    status: str
    description: str
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskResponseList(BaseModel):
    tasks: list[TaskResponse]

    model_config = ConfigDict(from_attributes=True)
