from models.database import _DATABASE


def reset_db(func):
    async def wrapper(*args, **kwargs):
        await _DATABASE.reset()
        await func(*args, **kwargs)

    return wrapper
