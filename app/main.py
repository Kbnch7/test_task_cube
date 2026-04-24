from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_healthchecks.api.router import HealthcheckRouter, Probe
from fastapi_healthchecks.checks.postgres import PostgreSqlCheck
from fastapi_healthchecks.checks.redis import RedisCheck

from app.api.api_router import main_router as router

from .config import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PORT,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    REDIS_PORT,
    REDIS_HOST
)
from .data.models import Base
from .data.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
app.include_router(
    HealthcheckRouter(
        Probe(
            name="readiness",
            checks=[
                PostgreSqlCheck(
                    host=DATABASE_HOST,
                    username=POSTGRES_USER,
                    password=POSTGRES_PASSWORD,
                    port=DATABASE_PORT,
                    database=DATABASE_NAME
                ),
                RedisCheck(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                ),
            ],
        ),
        Probe(
            name="liveness",
            checks=[]
        ),
    ),
    prefix="/health",
)
