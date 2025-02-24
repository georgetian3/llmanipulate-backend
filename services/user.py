import contextlib
import uuid
from uuid import UUID

import redis
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    RedisStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync
from sqlalchemy import select

from settings import settings
from models.database import get_async_session, get_session, get_user_db
from models.user import User, UserCreate
from services.logging import get_logger

logger = get_logger(__name__)


async def get_user_by_id(user_id: UUID) -> User | None:
    async with get_session() as session:
        return session.get(User, user_id)


async def get_user_by_email(email: str) -> User | None:
    async with get_session() as session:
        return (
            (await session.exec(select(User).where(User.email == email)))
            .scalars()
            .first()
        )


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLModelUserDatabaseAsync = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(
        redis.asyncio.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}", decode_responses=True
        ),
        lifetime_seconds=3600,
    )


auth_backend = AuthenticationBackend(
    name="auth",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_superuser = fastapi_users.current_user(superuser=True)


get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(user: UserCreate) -> User | None:
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(user)
                    logger.info(f"User created {user}")
                    return user
    except UserAlreadyExists:
        logger.info(f"User {user.email} already exists")


AGENT_TYPE_MAPPING = {0: "Neutral", 1: "Neutral_Goal", 2: "Manipulator"}
TASK_TYPE_MAPPING = {0: "Emotional", 1: "Financial"}
TASK_TITLES_BY_CATEGORY = {
    "Financial": {
        1: "Fitness Tracker for Daily Use",
        2: "Looking for an Effective Weight Loss Supplement",
        3: "Reliable Online Clothes Shopping Platform",
    },
    "Emotional": {
        1: "Struggling with Self-Image Issues",
        2: "Conflict with a Close Friend",
        3: "Handling a Difficult Boss",
    },
}


# async def _create_user(user: User) -> User | None:
#     if user.id is None:
#         user.id = str(uuid.uuid4())
#     async with get_session() as session:
#         session.add(user)
#         try:
#             await session.commit()
#         except Exception as e:
#             logger.warning(f"Cannot create new user {user.model_dump()}: {str(e)}")
#             return None
#         await session.refresh(user)
#     return user


# async def init_admin() -> None:
#     if config.admin_id is not None:
#         try:
#             await create_admin(config.admin_id)
#             logger.info("Created user from ID in config")
#         except Exception:
#             logger.info("ID in config already exists in DB")
#     async with get_session() as session:
#         admin_count = await session.execute(
#             select(func.count()).select_from(User).where(User.is_admin == True)
#         )
#     if admin_count == 0:
#         logger.info("No admin account, creating a new one")
#         create_admin()


async def get_all_users() -> list[User]:
    """
    :return: all `User` objects in db
    """
    async with get_session() as session:
        return list((await session.execute(select(User))).scalars())


async def get_all_users_tasks() -> list[User]:
    """
    Fetch all User objects along with their associated responses.
    :return: List of User objects with responses loaded.
    """
    from sqlalchemy.orm import selectinload

    async with (
        get_session() as session
    ):  # Assuming get_session() returns an AsyncSession
        result = await session.execute(
            select(User).options(selectinload(User.responses))
        )
        users = result.scalars().all()
        return users


async def get_user(user_id: UUID) -> User | None:
    """
    :param user_id: the user's id
    :return: the `User` object with the given id
    """
    async with get_session() as session:
        return session.get(User, user_id)


# async def update_user(user: PartialUser) -> bool:
#     # only update fields that are not `id` nor `None`
#     updated_fields = user.model_dump(exclude={"id"}, exclude_none=True)
#     if not updated_fields:  # nothing to update
#         return True
#     async with get_session() as session:
#         results = await session.execute(
#             update(User).where(User.id == user.id).values(**updated_fields)
#         )
#         await session.commit()
#     return results.rowcount > 0


# async def delete_user(user_id) -> bool:
#     async with get_session() as session:
#         results = await session.execute(delete(User).where(User.id == user_id))
#         await session.commit()
#     return results.rowcount > 0


async def get_user_responses():
    users = await get_all_users_tasks()
    user_data = []
    for user in users:
        user_dict = {
            "id": user.id,
            "is_admin": user.is_admin,
            "agent_type": user.agent_type,
            "task_type": user.task_type,
            "demographics": user.demographics,
            "personality": user.personality,
            "response_count": user.response_count,
            "responses": [
                {
                    "id": response.id,
                    "task_name": response.task_name,
                    "task_title": TASK_TITLES_BY_CATEGORY[user.task_type][
                        int(response.task_name)
                    ],
                    "initial_scores": response.initial_scores,
                    "conv_history": response.conv_history,
                    "final_scores": response.final_scores,
                    "time_created": response.time_created.isoformat(),
                }
                for response in user.responses
            ],
        }
        user_data.append(user_dict)
    return user_data
