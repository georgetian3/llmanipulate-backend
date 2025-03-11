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
from models.user import UserID
from services.logging import get_logger
from settings import settings

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
) -> tuple[TaskResponseRead | None, bool, bool]:
    """
    :returns:
        - TaskResponseRead | None: the newly created response
        - bool: task exists
        - bool: user is participant
    """
    logger.debug(f"User {user_id} submitting response for task {task_id}: {response}")
    if settings.user_correlation:
        query = (
            select(Task, TaskParticipant, TaskResponse)
            .outerjoin(
                TaskParticipant,
                (Task.id == task_id)  # type: ignore
                & (Task.id == TaskParticipant.task)
                & (TaskParticipant.user == user_id),
            )
            # if this where isn't added, the left join returns extra tasks
            .where(Task.id == task_id)
        )
    else:
        query = select(Task).where(Task.id == task_id)

    async with get_session() as session:
        result = (await session.execute(query)).first()

    if not result:  # task doesn't exist
        return None, False, False

    task = Task.model_validate(result[0])
    participant = TaskParticipant.model_validate(result[1]) if result[1] else None
    existing_response = TaskResponse.model_validate(result[2]) if result[2] else None

    if not participant:
        return None, True, False

    # validate the response checking that components have the right responses
    # if error exists, raises ValidationError that will be handled by FastAPI
    TaskResponseCreate.model_validate(
        response.model_dump(),
        context={
            "task_config": task.config,
            "existing_response": existing_response,
        },
    )

    response_db = TaskResponse(response=response.response, user=user_id, task=task.id)

    try:
        await response_db.save()
    except:
        return TaskResponse.get()

    async with get_session() as session:
        new_response = TaskResponseRead.model_validate(
            (await session.execute(upsert)).scalar_one()
        )
        await session.commit()

    return new_response, True, True


async def get_responses(task_id: TaskID) -> list[TaskResponseRead]:
    query = select(TaskResponse).where(TaskResponse.task == task_id)
    async with get_session() as session:
        return list((await session.execute(query)).all())
