import socket

from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=False, # для разработки, убрать потом
    pool_size=5,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except (SQLAlchemyError, socket.gaierror) as e:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        ) from e
