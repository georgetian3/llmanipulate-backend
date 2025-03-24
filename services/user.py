from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import delete, func, literal, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models.database import get_session
from models.models import to_model
from models.task import Task, TaskReadParticipant
from models.task_participant import TaskParticipant
from models.task_response import TaskResponse
from models.user import User, UserRead, UserUpsert
from services.logging import get_logger
from settings import SETTINGS

logger = get_logger(__name__)


async def create_admin(user_id: UUID4 | None = None) -> User:
    if user_id is None:
        user_id = uuid4()
    return await User(id=user_id, admin=True).save()


async def init_admin() -> None:
    if SETTINGS.admin_id is not None:
        try:
            await create_admin(SETTINGS.admin_id)
            logger.info("Created user from ID in settings")
        except Exception:
            logger.info("ID in settings already exists in DB")
    async with get_session() as session:
        admin_count = await session.execute(
            select(func.count()).select_from(User).where(User.admin == True)  # type: ignore
        )
    if admin_count == 0:
        logger.info("No admin account, creating a new one")
        await create_admin()


async def _upsert_create_user(user_upsert: UserUpsert) -> User:
    if not user_upsert.id:
        user_upsert.id = uuid4()
    if user_upsert.attributes is None:
        user_upsert.attributes = {}
    if user_upsert.active is None:
        user_upsert.active = True
    return await to_model(user_upsert, User).save()


async def upsert_user(user_upsert: UserUpsert) -> UserRead:
    # TODO: fix upsert concurrency bugs
    if not user_upsert.id:  # new user, no ID
        user = await _upsert_create_user(user_upsert)
    else:
        async with get_session() as session:
            user = await session.get(User, user_upsert.id)
            if user is None:  # new user, specific ID
                user = await _upsert_create_user(user_upsert)
            else:  # existing user
                if user_upsert.attributes is not None:
                    user.attributes = user_upsert.attributes
                if user_upsert.active is not None:
                    user.active = user_upsert.active
                await session.commit()
                await session.refresh(user)

    # dedup tasks
    # tasks that are both added and removed are not acted upon
    task_add = set(user_upsert.tasks_add)
    task_remove = set(user_upsert.tasks_remove)
    common = task_add & task_remove
    task_add -= common
    task_remove -= common

    # add user to tasks given that they exist and are private
    task_add_query = (
        pg_insert(TaskParticipant)
        .from_select(
            ["task_id", "user_id"],
            select(Task.id, literal(user_upsert.id)).where(
                Task.id.in_(task_add), Task.public == False
            ),
        )
        .on_conflict_do_nothing(index_elements=["task_id", "user_id"])
    )

    # remove users from tasks
    task_remove_query = delete(TaskParticipant).where(
        TaskParticipant.user_id == user_upsert.id,
        TaskParticipant.task_id.in_(task_remove),  # type: ignore
    )

    async with get_session() as session:
        await session.execute(task_add_query)
        await session.execute(task_remove_query)
        await session.commit()

    return to_model(user, UserRead)


async def get_user_tasks(user_id: UUID4) -> list[TaskReadParticipant]:
    logger.debug(f"Getting tasks for user {user_id}")
    query = (
        select(Task, TaskResponse)
        .outerjoin(TaskParticipant, TaskParticipant.task_id == Task.id)
        .outerjoin(TaskResponse, TaskResponse.task == Task.id)
        .where(Task.public | (TaskParticipant.user_id == user_id))
        .distinct(Task.id)
    )

    async with get_session() as session:
        results: list[tuple[Task, TaskResponse]] = (await session.execute(query)).all()

    return [
        TaskReadParticipant(
            config=task.config,
            id=task.id,
            completed=bool(response.user_id == user_id if response else False),
        )
        for task, response in results
    ]
