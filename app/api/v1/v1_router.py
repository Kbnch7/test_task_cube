from fastapi.routing import APIRouter

from .endpoints.tasks.tasks_router import tasks_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(tasks_router)
