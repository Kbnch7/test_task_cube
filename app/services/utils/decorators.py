from functools import wraps

from sqlalchemy.exc import SQLAlchemyError

from app.services.utils.exceptions import DatabaseError, TaskNotFoundError


def catch_sqlalchemy_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            raise DatabaseError from e
    return wrapper

def catch_task_not_found_error(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if result is None:
            raise TaskNotFoundError()
        return result
    return wrapper
