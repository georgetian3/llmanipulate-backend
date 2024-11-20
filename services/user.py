import uuid

from sqlalchemy import select

from models.database import get_session
from models.models import NewUser, User


async def _create_user(user: User) -> User:
    user.id = str(uuid.uuid4())
    async with get_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def create_user(new_user: NewUser) -> User:
    """
    Creates a user
    :param new_user: the new user to be created
    :return: newly created `User` object
    """
    return await _create_user(User(**new_user.model_dump(), is_admin=False))


async def create_admin() -> User:
    return await _create_user(
        User(task_type="admin", agent_type="admin", is_admin=True)
    )


async def get_all_users() -> list[User]:
    """
    :return: all `User` objects in db
    """
    async with get_session() as session:
        return list((await session.execute(select(User))).scalars())
