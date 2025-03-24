from uuid import uuid4

# from models.chat import Agent
from models.database import _DATABASE
from models.task import TaskCreate
from models.task_config.base_component import Translations
from models.task_config.chat import AgentConfig, ChatConfig
from models.task_config.task_config import ComponentGroup, TaskConfig, TaskPage
from services.tasks import create_task


async def test_create_task() -> None:
    await _DATABASE.reset()

    task_create = TaskCreate(
        config=TaskConfig(
            name=Translations(languages={"en": "sample task name"}),
            pages=[
                TaskPage(
                    component_groups=[
                        ComponentGroup(
                            components=[
                                ChatConfig(
                                    id="chat",
                                    agents=[
                                        AgentConfig(
                                            display_name="Agent 1",
                                        ),
                                        AgentConfig(
                                            display_name="Agent 2",
                                        ),
                                    ],
                                )
                            ]
                        )
                    ]
                )
            ],
            public=True,
        )
    )
    task_read = await create_task(task_create)
    assert (
        isinstance(task_read.config, TaskConfig)
        and task_read.config == task_create.config
        and task_read.public == task_create.config.public
    )
    # # check all agent rows are created
    # agents = await Agent.all()
    # assert set(
    #     agent.display_name
    #     for page in task_create.config.pages
    #     for group in page.component_groups
    #     for component in group.components
    #     for agent in component.agents
    #     if component.type == "chat"
    # ) == set(agent.display_name for agent in agents)


# async def test_add_participant_to_public_task() -> None:
#     await _DATABASE.reset()

#     task_public = await create_task(TaskCreate(
#         config=TaskConfig(
#             name=Translations(languages={"en": "sample task name"}),
#             pages=[],
#             public=True,
#         )
#     ))
#     task_private = await create_task(TaskCreate(
#         config=TaskConfig(
#             name=Translations(languages={"en": "sample task name"}),
#             pages=[],
#             public=False,
#         )
#     ))

#     existing_user = await upsert_user(UserUpsert())
#     public_user_id = uuid4()

#     await add_participant_to_public_task(task_private.id, existing_user.id)
#     assert len(await TaskParticipant.all()) == 0
#     await add_participant_to_public_task(task_private.id, public_user_id)
#     assert len(await TaskParticipant.all()) == 0
#     await add_participant_to_public_task(task_public.id, existing_user.id)
#     assert len(await TaskParticipant.all()) == 1
#     await add_participant_to_public_task(task_public.id, public_user_id)
#     assert len(await TaskParticipant.all()) == 2

