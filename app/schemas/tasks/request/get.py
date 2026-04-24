from uuid import UUID

from pydantic import BaseModel


class TaskGet(BaseModel):
    id: UUID
