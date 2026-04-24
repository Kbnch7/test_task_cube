from uuid import UUID

from pydantic import BaseModel


class TaskGet(BaseModel):
    id: UUID

class Pagination(BaseModel):
    skip: int = 0
    limit: int = 100
