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


def validate_response(
    task_config: TaskConfig,
    new_response: TaskResponseCreate,
    existing_response: TaskResponse | None,
) -> None:
    all_components_responded = True
    # for each component in a task config
    for component in task_config.components:
        # get the response for this compoment
        component_response = new_response.response.get(component.id)
        # if the response for this component is missing
        if component_response is None:
            all_components_responded = False
            # new response cannot have less answers than the old response
            if (
                # a non-draft response cannot have empty component responses
                not new_response.draft
                # if a response for this component in an older draft exists, new draft cannot be missing this response
                or existing_response
                and component.id not in existing_response.response
            ):
                raise ValueError(f"Component '{component.id}': missing response")
        else:
            # let each component validate the type/structure of its response
            try:
                component.validate_response(component_response)
            except ValueError as e:
                raise ValueError(f"Component '{component.id}': {e}") from e
    if all_components_responded:
        new_response.draft = False


async def create_response(
    task_id: UUID4, response: TaskResponseCreate, user: User
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
            & (TaskParticipant.user == user.id),
        )
        # gets the draft response if it exists
        .outerjoin(
            TaskResponse,
            (Task.id == TaskResponse.task) & (TaskResponse.user == user.id),  # type: ignore
        )
    )
    async with get_session() as session:
        result: tuple[Task, TaskParticipant, TaskResponse] | None = (
            await session.execute(query)
        ).first()

    if not result:  # task doesn't exist
        return None, False, False, None

    task, participant, existing_response = result
    if not participant:
        return None, True, False, None
    try:
        validate_response(task.config, response, existing_response)
    except Exception as e:
        logger.exception("Exception")
        return None, True, True, str(e)

    upsert = (
        insert(TaskResponse)
        .on_conflict_do_update(
            index_elements=["task", "user"],
            set_={"draft": response.draft, "response": response.response},
        )
        .returning(TaskResponse)
    )

    async with get_session() as session:
        new_response = (await session.execute(upsert)).scalar_one()
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
