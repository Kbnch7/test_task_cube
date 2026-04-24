import datetime
import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseTable(Base):
    __abstract__ = True

class Users(Base):
    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    username = Column(String(20), unique=True, nullable=False)


class Task(Base):
    __tablename__ = 'task'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        server_default=text("gen_random_uuid()")
    )
    title = Column(String(20), nullable=False)
    description = Column(String(200), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    status = Column(String(20), nullable=False, default="todo")
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())
