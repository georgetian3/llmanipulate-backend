from pydantic import UUID4
from sqlalchemy import func, select

from models.database import get_session
from models.user import User, UserCreate, UserRead
from services.logging import get_logger
from settings import SETTINGS

logger = get_logger(__name__)


async def create_admin(user_id: UUID4 | None) -> User:
    return await User(id=user_id, is_admin=True).save()


async def init_admin() -> None:
    if SETTINGS.admin_id is not None:
        try:
            await create_admin(SETTINGS.admin_id)
            logger.info("Created user from ID in settings")
        except Exception:
            logger.info("ID in settings already exists in DB")
    async with get_session() as session:
        admin_count = await session.execute(
            select(func.count()).select_from(User).where(User.is_admin == True)
        )
    if admin_count == 0:
        logger.info("No admin account, creating a new one")
        await create_admin()


async def create_participant(user_create: UserCreate | None) -> UserRead:
    user = await User.model_validate(user_create).save()
    return UserRead.model_validate(user)


async def get_all_users() -> list[UserRead]:
    async with get_session() as session:
        return [
            UserRead.model_validate(user)
            for user in (await session.execute(select(User))).scalars()
        ]


# async def get_all_users_tasks() -> list[User]:
#     """
#     Fetch all User objects along with their associated responses.
#     :return: List of User objects with responses loaded.
#     """
#     from sqlalchemy.orm import selectinload

#     async with (
#         get_session() as session
#     ):  # Assuming get_session() returns an AsyncSession
#         result = await session.execute(
#             select(User).options(selectinload(User.responses))
#         )
#         users = result.scalars().all()
#         return users


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


# async def get_user_responses():
#     users = await get_all_users_tasks()
#     user_data = []
#     for user in users:
#         user_dict = {
#             "id": user.id,
#             "is_admin": user.is_admin,
#             "agent_type": user.agent_type,
#             "task_type": user.task_type,
#             "demographics": user.demographics,
#             "personality": user.personality,
#             "response_count": user.response_count,
#             "responses": [
#                 {
#                     "id": response.id,
#                     "task_name": response.task_name,
#                     "task_title": TASK_TITLES_BY_CATEGORY[user.task_type][
#                         int(response.task_name)
#                     ],
#                     "initial_scores": response.initial_scores,
#                     "conv_history": response.conv_history,
#                     "final_scores": response.final_scores,
#                     "time_created": response.time_created.isoformat(),
#                 }
#                 for response in user.responses
#             ],
#         }
#         user_data.append(user_dict)
#     return user_data
