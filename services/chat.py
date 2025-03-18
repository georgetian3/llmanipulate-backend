# import json

# from models.database import get_session
# from models.models import LLMInput, LLMResponse
# from models.user import User
# from services.agent import Agent
# from services.tasks import Task

# lang_dict = json.load(open("services/data/lang.json", "r", encoding="utf-8"))["BFI"]


# def parse_personality(personality, lang):
#     p_str = []
#     for key, value in personality.items():
#         value = float(value)
#         level = f"{'High' if value >= 5.5 else ('Moderate' if value >= 3 else 'Low')}"
#         p_str.append(
#             f"{lang_dict[level][lang]}{' ' if lang == 'en' else ''}{lang_dict[key][lang]}"
#         )
#     return ", ".join(p_str)


# async def config_agent(llmp_input: LLMInput):
#     agent = Agent()

#     model_name = "gpt-4o"
#     async with get_session() as session:
#         user = await session.get(User, llmp_input.user_id)
#     if user is None:
#         raise Exception("User not found")

#     language = user.demographics.get("lang")
#     user_personality = user.personality

#     # task = Task()
#     # task_type = user.task_type
#     # task_id = llmp_input.task_id

#     # tasks = json.loads(open("services/data/tasks.json", "r", encoding="utf-8").read())
#     # task_by_type = tasks.get(task_type)
#     # task_by_id = next(
#     #     (task for task in task_by_type if task["task_id"] == int(task_id)), None
#     # )

#     # task.set_attributes(
#     #     _id=task_by_id["task_id"],
#     #     title=task_by_id["query"]["title"],
#     #     desc=task_by_id["query"]["desc"],
#     #     options=task_by_id["options"],
#     #     hidden_incentive=task_by_id["hidden_incentive"],
#     #     lang=language,
#     # )
#     # task.sort_options(llmp_input.map)

#     # agent_type = user.agent_type
#     # user_personality = parse_personality(user_personality, language)
#     # agent.set_attributes(model_name, agent_type, language, user_personality)
#     # agent.set_task(task)
#     agent.fill_prompt()
#     return agent


# async def get_llm_response(llm_input: LLMInput, agent: Agent) -> LLMResponse:
#     msg = {"role": "user", "content": llm_input.message}

#     full_response = agent.generate(msg).get("content")
#     response = full_response.get("response")
#     del full_response["response"]

#     return LLMResponse(response=response, agent_data=full_response)


# """

# To test  ***
# async def main():
#     tasks = json.loads(open("services/data/tasks.json", "r").read())
#     print("Hello")
#     llm_input = LLMInput(user_id="1", task_id=1, message="Hello")
#     agent = await config_agent(llm_input)
#     response_id = await create_response(llm_input.user_id, llm_input.task_id)

#     response1 = await get_llm_response(llm_input, agent, response_id)
#     print(response1)
#     print("you tell me")
#     llm_input2 = LLMInput(user_id="1", task_id=1, message="you tell me")
#     response2 = await get_llm_response(llm_input2, agent, response_id)
#     print(response2)

# asyncio.run(main())
# """


import asyncio
from dataclasses import dataclass
from uuid import uuid4

from fastapi import WebSocket
from pydantic import UUID4, BaseModel, ValidationError
from sqlalchemy import func, null, select

from models.chat import (
    Chat,
    ChatMessage,
    ChatMessageRead,
    ChatParticipant,
    ChatParticipantRead,
    WebsocketReceive,
    WebsocketSend,
)
from models.database import get_session
from models.task import Task, TaskParticipant
from models.task_config.chat import ChatConfig
from services.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChatWebsocket:
    websocket: WebSocket
    user_id: UUID4
    task_id: UUID4
    component_id: str
    chat_id: UUID4 | None = None


class WebsocketChatManager:
    def __init__(self):
        self.chat_configs: dict[UUID4, dict[str, ChatConfig]] = {}
        self.chats: dict[UUID4, set[WebSocket]] = {}

    async def connect(self, websocket: ChatWebsocket) -> bool:
        user_id, task_id, component_id = websocket.user_id, websocket.task_id, websocket.component_id
        # 1. check user is member of task
        # 2. if user is not in this task component's chat
        # 3.    find chat that needs another participant, or create new chat
        # 4. return chat's history

        # chat_participant_query = (
        #     select(Task, Chat, ChatParticipant)
        #     .join(TaskParticipant, TaskParticipant.task == task_id)
        #     .outerjoin(Chat, Chat.task == Task.id)
        #     .outerjoin(ChatParticipant, ChatParticipant.chat_id == Chat.id)
        #     .where(
        #         TaskParticipant.user == user_id,
        #         TaskParticipant.task == task_id,
        #         Chat.component == component_id,
        #     )
        # )
        logger.debug(
            f"Websocket connect user_id={user_id} task_id={task_id} component_id={component_id}"
        )
        task_query = (
            select(Task)
            .join(TaskParticipant, Task.id == TaskParticipant.task)
            .where(Task.id == task_id)
        )
        async with get_session() as session:
            task = (await session.scalars(task_query)).first()

        if not task:
            logger.debug(
                f"Task {task_id} does not exist or user {user_id} is not a participant"
            )
            await websocket.websocket.close()
            return False

        try:
            chat_config = [
                x
                for x in task.config.components
                if x.id == component_id and x.type == "chat"
            ][0]
        except:  # chat component doesn't exist
            logger.debug(f"Component {component_id} does not exist for task {task_id}")
            await websocket.websocket.close()
            return False

        # user allowed to chat
        await websocket.websocket.accept()

        existing_chat_select_query = (
            select(Chat)
            .join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
            .where(
                ChatParticipant.user_id == user_id,
                Chat.task_id == task_id,
                Chat.component_id == component_id,
            )
        )
        async with get_session() as session:
            chat = (
                await session.execute(existing_chat_select_query)
            ).scalar_one_or_none()
            if chat:  # already participant of a chat, send chat messages
                logger.debug(f"User {user_id} already participant in chat {chat.id}")
                chat_messages_select_query = select(ChatMessage).where(
                    ChatMessage.chat_id == chat.id
                )
                chat_participants_query = select(ChatParticipant).join(
                    Chat, (ChatParticipant.chat_id == chat.id) & (Chat.id == chat.id)
                )
                results: list[tuple[ChatMessage, ChatParticipant]] = (
                    await session.execute(chat_messages_select_query)
                ).all()
                chat_participants = (
                    await session.scalars(chat_participants_query)
                ).all()
                chat_messages = []
                for result in results:
                    chat_message, chat_participant = result
                    chat_messages.append(
                        ChatMessageRead(
                            id=chat_message.id,
                            chat_id=chat.id,
                            message=chat_message.message,
                            timestamp=chat_message.timestamp,
                            sender=chat_participant.name,
                        )
                    )
                await self.send_to_websocket(
                    WebsocketSend(
                        chat_id=chat.id,
                        messages=chat_messages,
                        participants=[
                            ChatParticipantRead(name=cp.name)
                            for cp in chat_participants
                        ],
                    ),
                    websocket,
                )
                return True
        if chat_config.humans_required is None:  # task-wide chat, only one should exist
            pending_chat_select_query = select(Chat).where(
                Chat.task_id == task_id, Chat.component_id == component_id
            )
        elif (
            chat_config.humans_required == 1
        ):  # one human chat, there should not be an existing one
            pending_chat_select_query = select(null())
        else:
            pending_chat_select_query = (
                select(Chat)
                .join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
                .group_by(Chat.id)
                .having(func.count(ChatParticipant) < chat_config.humans_required)
                .limit(1)
            )
        async with get_session() as session:
            pending_chat: Chat | None = (
                await session.execute(pending_chat_select_query)
            ).scalar_one_or_none()
            if not pending_chat:
                pending_chat = Chat(task_id=task_id, component_id=component_id)
                session.add(pending_chat)
            session.add(
                ChatParticipant(name="", user_id=user_id, chat_id=pending_chat.id)
            )
            await session.commit()
            await session.refresh(pending_chat)
            await self.send_to_websocket(
                WebsocketSend(
                    chat_id=pending_chat.id,
                    messages=[],
                    participants=[ChatParticipantRead(name="self")],
                ),
                websocket,
            )
        return True

    async def receive(self, json: dict, websocket: ChatWebsocket) -> None:
        try:
            data = WebsocketReceive.model_validate(json)
        except ValidationError as e:
            await websocket.websocket.send_json(WebsocketSend(error=str(e)))
            return
        logger.debug(f"Websocket {websocket} received: {data}")
        await self.send_to_chat(data, 1)

    async def send_to_websocket(self, data: WebsocketSend, websocket: ChatWebsocket):
        logger.debug(f"Sending to websocket {websocket} data {data}")
        await websocket.websocket.send_text(data.model_dump_json())

    async def send_to_chat(self, data: WebsocketSend, chat_id: UUID4) -> None:
        logger.debug(f"Sending to chat {chat_id} data {data}")
        data_json = data.model_dump_json()
        futures = [ws.send_text(data_json) for ws in self.chats[chat_id]]
        await asyncio.gather(*futures)

    async def disconnect(self, websocket: WebSocket) -> None:
        await websocket.close()
