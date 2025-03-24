from uuid import uuid4

from models.task_response import TaskResponseCreate
from services.responses import create_response


async def test_create_response(sample_data) -> None:
    creator, participant, task, task_participant = sample_data

    good_response = TaskResponseCreate(draft=True, response={"1": "free text response"})

    # new response
    (
        response_read,
        task_exists,
        is_participant,
        validation_error,
    ) = await create_response(
        task_id=task.id,
        existing_response=good_response,
        user_id=participant.id,
    )

    # updated response
    (
        response_read,
        task_exists,
        is_participant,
        validation_error,
    ) = await create_response(
        task_id=task.id,
        existing_response=good_response,
        user_id=participant.id,
    )

    assert (
        response_read is not None
        and task_exists
        and is_participant
        and validation_error is None
    )

    # task doesn't exist
    (
        response_read,
        task_exists,
        is_participant,
        validation_error,
    ) = await create_response(
        task_id=uuid4(),
        existing_response=good_response,
        user_id=participant.id,
    )

    assert (
        response_read is None
        and task_exists == False
        and is_participant == False
        and validation_error is None
    )

    # user doesn't exist
    (
        response_read,
        task_exists,
        is_participant,
        validation_error,
    ) = await create_response(
        task_id=task.id,
        existing_response=good_response,
        user_id=uuid4(),
    )

    assert (
        response_read is None
        and task_exists == True
        and is_participant == False
        and validation_error is None
    )
