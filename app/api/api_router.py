from fastapi.routing import APIRouter

from .v1.v1_router import v1_router

main_router = APIRouter()
main_router.include_router(v1_router)
