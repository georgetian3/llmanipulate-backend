from pydantic import UUID4, ValidationError
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
from models.user import User, UserID
from services.logging import get_logger

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
    task_id: UUID4, response: TaskResponseCreate, user_id: UserID
) -> tuple[TaskResponseRead | None, bool, bool, str | None]:
    """
    :returns:
        - TaskResponseRead | None: the newly created response
        - bool: task exists
        - bool: user is participant
        - str | None: response validation error
    """
    query = (
        select(Task, TaskParticipant, TaskResponse)
        # ensures the user is a participant of the task
        .outerjoin(
            TaskParticipant,
            (Task.id == task_id)  # type: ignore
            & (Task.id == TaskParticipant.task)
            & (TaskParticipant.user == user_id),
        )
        # gets the draft response if it exists
        .outerjoin(
            TaskResponse,
            (Task.id == TaskResponse.task) & (TaskResponse.user == user_id),  # type: ignore
        )
        # if this where isn't added, the left join returns extra tasks
        .where(Task.id == task_id)
    )
    async with get_session() as session:
        result = (await session.execute(query)).first()

    if not result:  # task doesn't exist
        return None, False, False, None

    task = Task.model_validate(result[0])
    participant = TaskParticipant.model_validate(result[1]) if result[1] else None
    existing_response = TaskResponse.model_validate(result[2]) if result[2] else None

    if not participant:
        return None, True, False, None
    try:
        # validate the response checking that components have the right responses
        TaskResponseCreate.model_validate(
            response.model_dump(),
            context={
                "task_config": task.config,
                "existing_response": existing_response,
            },
        )
    except ValidationError as e:
        logger.exception("Validation error")
        return None, True, True, str(e)

    response_db = TaskResponse(
        draft=response.draft, response=response.response, user=user_id, task=task.id
    )

    upsert = (
        insert(TaskResponse)
        .values(response_db.model_dump())
        .on_conflict_do_update(
            # index on primary keys
            index_elements=["task", "user"],
            # only update the following fields
            set_=response_db.model_dump(
                include={"draft", "response", "updated_timestamp"}
            ),
            # only update if this response is newer
            where=TaskResponse.updated_timestamp < response_db.updated_timestamp,
        )
        .returning(TaskResponse)
    )

    async with get_session() as session:
        new_response = TaskResponseRead.model_validate(
            (await session.execute(upsert)).scalar_one()
        )
        await session.commit()

    return new_response, True, True, None


async def get_responses(task_id: TaskID, user_id: UserID) -> list[TaskResponseRead]:
    query = select(TaskResponse).join(
        Task,
        (Task.id == task_id)  # type: ignore
        & (Task.creator == user_id)
        & (TaskResponse.task == Task.id),
    )
    async with get_session() as session:
        task_responses = list((await session.execute(query)).all())
    return task_responses
