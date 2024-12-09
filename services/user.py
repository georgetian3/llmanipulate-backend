import asyncio
import logging
import uuid

from sqlalchemy import delete, select, func, update

from config import AuthConfig
from models.database import get_session
from models.models import NewUser, PartialUser, User
from services.logging import get_logger

logger = get_logger()

AGENT_TYPE_MAPPING= {0:"Neutral", 1:"Neutral_Goal", 2:"Manipulator"}
TASK_TYPE_MAPPING = {0: "Emotional", 1:"Financial"}
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
    user = User(
        demographics=new_user.demographics,
        personality=new_user.personality,
        task_type=TASK_TYPE_MAPPING[new_user.task_type],
        agent_type=AGENT_TYPE_MAPPING[new_user.agent_type],
        is_admin=False
    )
    return await _create_user(user)


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

async def get_user(user_id: str) -> User | None:
    """
    :param user_id: the user's id
    :return: the `User` object with the given id
    """
    async with get_session() as session:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
async def update_user(user: PartialUser) -> bool:
    # only update fields that are not `id` nor `None`
    updated_fields = user.model_dump(exclude={'id'}, exclude_none=True)
    if not updated_fields: # nothing to update
        return True
    async with get_session() as session:
        results = await session.execute(
            update(User)
                .where(User.id == user.id)
                .values(**updated_fields)
        )
        await session.commit()
    return results.rowcount > 0

async def delete_user(user_id) -> bool:
    async with get_session() as session:
        results = await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
    return results.rowcount > 0

