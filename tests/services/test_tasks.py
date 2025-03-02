from uuid import uuid4

import pytest

from models.database import _DATABASE
from services.tasks import get_participant_tasks, get_task
from tests.conftest import sample_data


async def test_get_tasks(sample_data):
    creator, participant, task, task_participant = sample_data
    # user is task participant
    assert await get_task(task.id, participant.id) == (task, True)
    # user is task creator
    assert await get_task(task.id, creator.id) == (task, True)
    # user is neither
    assert await get_task(task.id, uuid4()) == (task, False)
    # task doesn't exist
    assert await get_task(uuid4(), uuid4()) == (None, None)

async def test_get_participant_tasks(sample_data):
    creator, participant, task, task_participant = sample_data
    await get_participant_tasks(participant.id)

