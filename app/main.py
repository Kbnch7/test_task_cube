from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_healthchecks.api.router import HealthcheckRouter, Probe
from fastapi_healthchecks.checks.postgres import PostgreSqlCheck
from fastapi_healthchecks.checks.redis import RedisCheck
from sqlalchemy import select

from app.api.api_router import main_router as router
from app.data.models import Users
from app.data.session import AsyncSessionLocal

from .config import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PORT,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    REDIS_HOST,
    REDIS_PORT,
)
from .data.models import Base
from .data.session import engine


async def create_initial_users():
    async with AsyncSessionLocal() as session:
        users_data = [
            {"id": "f2d51619-ee0d-40e7-86a9-c6cf1314c3b6", "username": "user1"},
            {"id": "a0c655d3-7065-4e0c-aea6-fa0ad79c59df", "username": "user2"}
        ]
        for user_info in users_data:
            stmt = select(Users).where(Users.id == user_info["id"])
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                session.add(Users(**user_info))
        await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_initial_users()
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
