from uuid import UUID

from pydantic import BaseModel


class TaskDelete(BaseModel):
    id: UUID
