from uuid import uuid4
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from models.database import get_session
from models.task import (
    Task,
    TaskID,
    TaskParticipant,
    TaskResponse,
    TaskResponseCreate,
    TaskResponseRead,
)
from models.task_config.task_config import TaskConfig
from models.user import UserID
from services.logging import get_logger
from settings import SETTINGS

logger = get_logger(__name__)


# async def create_response(
#     response_create: ResponseCreate, user: User
# ) -> Response | None:
#     try:
#         response = Response(response_create, user_id=user.id)
#         async with get_session() as session:
#             result = await session.execute(
#                 select(Response).filter_by(
#                     user_id=response.user_id, task_name=response.task_name
#                 )
#             )
#             existing_response = result.scalars().first()

#             # If the response exists, return it without creating a new one
#             if existing_response:
#                 return existing_response

#             # Create a new response if none exists
#             new_response = Response(
#                 user_id=response.user_id,
#                 task_name=response.task_name,
#                 initial_scores=response.initial_scores,
#                 conv_history=response.conv_history,
#                 final_scores=response.final_scores,
#                 time_created=datetime.now(UTC),
#             )

#             session.add(new_response)
#             await session.commit()
#             await session.refresh(new_response)

#             return new_response

#     except Exception as e:
#         logger.exception(f"Create response exception: {e}")
#         return None


# async def get_responses_by_users(user_id: str):
#     async with get_session() as session:
#         try:
#             # Use select() for querying in async mode
#             stmt = select(Response).where(Response.user_id == user_id)
#             result = await session.execute(stmt)
#             responses = result.scalars().all()

#             if not responses:
#                 return {"error": "No responses found for the given user_id"}

#             # Return the responses as a list of dictionaries
#             return responses

#         except Exception as e:
#             return {"error": f"Error fetching responses from database: {str(e)}"}


# async def get_responses():
#     async with get_session() as session:
#         try:
#             stmt = select(Response)
#             result = await session.execute(stmt)
#             responses = result.scalars().all()

#             if not responses:
#                 return {"error": "No responses found"}

#             return responses

#         except Exception as e:
#             return {"error": f"Error fetching responses from database: {str(e)}"}


async def create_response(
    task_id: UUID4, response: TaskResponseCreate, user_id: UserID | None
) -> tuple[TaskResponseRead | None, bool, bool, bool]:
    """
    :returns:
        - TaskResponseRead | None: the newly created response
        - bool: task exists
        - bool: user is participant
        - bool: task already completed
    """
    logger.debug(f"User {user_id} submitting response for task {task_id}: {response}")
    query = (
        select(Task, TaskParticipant, TaskResponse)
        .outerjoin(
            TaskParticipant,
            (Task.id == TaskParticipant.task) & (TaskParticipant.user == user_id),
        )
        .outerjoin(
            TaskResponse,
            (TaskResponse.task == task_id) & (TaskResponse.user == user_id),
        )
        # if this where isn't added, the left join returns extra tasks
        .where(Task.id == task_id)
    )

    async with get_session() as session:
        results: tuple[Task | None, TaskParticipant | None, TaskResponse | None] = (
            await session.execute(query)
        ).first()

    if not results:
        return None, False, False

    task, is_participant, existing_response = results
    task.config = TaskConfig.model_validate(task.config)

    if task.config.login_required:
        if not is_participant:
            return None, True, False, False
        if existing_response:
            return existing_response, True, True, True
    else:  # if no login required, randomize user_id
        user_id = uuid4()

    response_db = TaskResponse(response=response.response, user=user_id, task=task.id)

    print('here', response_db.model_dump())

    try:
        return (
            TaskResponseRead.model_validate(await response_db.save()),
            True,
            True,
            False,
        )
    except Exception as e:
        logger.info("Error saving response:", e)
        return (
            None,
            True,
            True,
            True,
        )


async def get_responses(task_id: TaskID) -> list[TaskResponseRead]:
    query = select(TaskResponse).where(TaskResponse.task == task_id)
    async with get_session() as session:
        return list((await session.execute(query)).all())
