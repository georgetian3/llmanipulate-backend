import asyncio
import logging
import uuid

from sqlalchemy import select, func

from config import AuthConfig
from models.database import get_session
from models.models import NewUser, User
from services.logging import get_logger

logger = get_logger()


async def _create_user(user: User) -> User:
    if user.id is None:
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


async def create_admin(id: str = None) -> User:
    return await _create_user(
        User(id=id, task_type="admin", agent_type="admin", is_admin=True)
    )

async def init_admin() -> None:
    if AuthConfig.ADMIN_ID is not None:
        try:
            await create_admin(AuthConfig.ADMIN_ID)
            logger.info('Created user from ID in config')
        except Exception as e:
            logger.info(f'ID in config already exists in DB')
    async with get_session() as session:
        admin_count = await session.execute(
            select(func.count()).select_from(User).where(User.is_admin==True)
        )
    if admin_count == 0:
        logger.info(f'No admin account, creating a new one')
        create_admin()

asyncio.run(init_admin())


async def get_all_users() -> list[User]:
    """
    :return: all `User` objects in db
    """
    async with get_session() as session:
        return list((await session.execute(select(User))).scalars())

async def get_user(user_id: str):
    """
    :param user_id: the id of the user to be fetched
    :return: the `User` object with the given id
    """
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        if result is None:
            return {"error": "User not found"}
        return result.scalar()