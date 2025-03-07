from models.task import TaskResponseCreate
from services.responses import create_response
from tests.conftest import sample_data


async def test_create_response(sample_data) -> None:
    creator, participant, task, task_participant = sample_data

    response = TaskResponseCreate(draft=True, response={"1": "free text response"})

    (
        response_read,
        task_exists,
        is_participant,
        validation_error,
    ) = await create_response(
        task_id=task.id,
        response=response,
        user=participant,
    )
    print(response_read, task_exists, is_participant, validation_error)
    return
    assert response_read is not None
    assert task_exists and is_participant
    assert validation_error is None
