from uuid import uuid4

import httpx
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from apis import api
from models.chat import Chat, ChatMessage, ChatParticipant, WebsocketSend
from models.database import _DATABASE
from models.task import TaskCreate, TaskRead
from models.task_config.agent import AgentConfig
from models.task_config.base_component import Translations
from models.task_config.chat import ChatConfig
from models.task_config.task_config import ComponentGroup, TaskConfig, TaskPage
from services.logging import get_logger
from services.tasks import create_task, get_task

logger = get_logger(__name__)


async def create_chat_test_task(chat_config: ChatConfig) -> TaskRead:
    return await create_task(
        TaskCreate(
            config=TaskConfig(
                name=Translations(languages={"en": "sample task name"}),
                pages=[
                    TaskPage(
                        component_groups=[ComponentGroup(components=[chat_config])]
                    )
                ],
                public=True,
            )
        )
    )


# async def test_chat_1_human_1_agent() -> None:
#     await _DATABASE.reset()
#     task = await create_chat_test_task(
#         ChatConfig(
#             id="chat",
#             agents=[AgentConfig(id="agent", type="TestAgent", display_name="Agent")],
#             humans_required=1,
#             order=["human", "agent"],
#         )
#     )
#     user_id = uuid4()
#     await get_task(task.id, user_id)
#     async with httpx.AsyncClient(
#         transport=ASGIWebSocketTransport(api), base_url="http://test"
#     ) as client:
#         async with aconnect_ws(
#             f"http://test/chat?user={user_id}&task={task.id}&component=chat", client
#         ) as ws:
#             message = WebsocketSend.model_validate_json(await ws.receive_text())

#     # TODO: continue assertions after chat order logic is implemented


async def test_chat_2_humans() -> None:
    await _DATABASE.reset()
    task = await create_chat_test_task(
        ChatConfig(
            id="chat",
            agents=[AgentConfig(id="agent", type="TestAgent", display_name="Agent")],
            humans_required=2,
            order=["human", "agent", "human"],
        )
    )
    user_ids = [uuid4() for _ in range(3)]
    for user_id in user_ids:
        await get_task(task.id, user_id)

    async with httpx.AsyncClient(
        transport=ASGIWebSocketTransport(api), base_url="http://test"
    ) as client:
        # 1st user joins, creates new chat
        async with aconnect_ws(
            f"http://test/chat?user={user_ids[0]}&task={task.id}&component=chat", client
        ) as ws:
            message = WebsocketSend.model_validate_json(await ws.receive_text())

        chats = await Chat.all()
        assert len(chats) == 1
        chat = chats[0]
        assert chat.task_id == task.id
        assert chat.id == message.chat_id
        assert len(await ChatMessage.all()) == 0
        chat_participants = await ChatParticipant.all()
        assert len(chat_participants) == 1
        chat_participant = chat_participants[0]
        assert chat_participant.user_id == user_ids[0]

        # 2nd user joins the same chat
        async with aconnect_ws(
            f"http://test/chat?user={user_ids[1]}&task={task.id}&component=chat", client
        ) as ws:
            message = WebsocketSend.model_validate_json(await ws.receive_text())

        assert len(await Chat.all()) == 1
        assert len(await ChatParticipant.all()) == 2

        # 3rd user joins new chat
        async with aconnect_ws(
            f"http://test/chat?user={user_ids[2]}&task={task.id}&component=chat", client
        ) as ws:
            message = WebsocketSend.model_validate_json(await ws.receive_text())

        assert len(await Chat.all()) == 2
        assert len(await ChatParticipant.all()) == 3

        # TODO: continue assertions after chat order logic is implemented
