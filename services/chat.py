import asyncio
from dataclasses import astuple, dataclass, field
from uuid import uuid4

from fastapi import WebSocket
from pydantic import UUID4, ValidationError
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
from models.task import Task
from models.task_config.chat import ChatConfig
from models.task_participant import TaskParticipant
from services.agentV2 import Agent
from services.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChatState:
    chat_id: UUID4
    task_id: UUID4
    component_id: str
    # map of user id to websocket
    websockets: dict[UUID4, WebSocket] = field(default_factory=dict)
    # map of agent ID (from task config) to agent instance
    agents: dict[str, Agent] = field(default_factory=dict)


class WebsocketChatManager:
    def __init__(self):
        self.chats: dict[UUID4, ChatState] = {}

    async def connect(
        self, websocket: WebSocket, user_id: UUID4, task_id: UUID4, component_id: str
    ) -> bool:
        logger.debug(
            f"Websocket connect user_id={user_id} task_id={task_id} component_id={component_id}"
        )
        task_query = (
            select(Task)
            .join(
                TaskParticipant,
                Task.id == TaskParticipant.task_id,
            )
            .where(Task.id == task_id, TaskParticipant.user_id == user_id)
        )
        async with get_session() as session:
            task = (await session.scalars(task_query)).first()

        if not task:
            logger.debug(
                f"Task {task_id} does not exist or user {user_id} is not a participant"
            )
            await websocket.close()
            return False
        task.parse_config()
        try:
            chat_config = [
                x
                for x in task.config.components
                if x.id == component_id and x.type == "chat"
            ][0]
        except:  # chat component doesn't exist
            logger.debug(f"Component {component_id} does not exist for task {task_id}")
            await websocket.close()
            return False

        # user allowed to chat
        await websocket.accept()

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
            existing_chat = (
                await session.execute(existing_chat_select_query)
            ).scalar_one_or_none()
            if existing_chat:  # already participant of a chat, send chat messages
                logger.debug(
                    f"User {user_id} already participant in chat {existing_chat.id}"
                )
                chat_messages_select_query = select(ChatMessage).where(
                    ChatMessage.chat_id == existing_chat.id
                )
                chat_participants_query = select(ChatParticipant).join(
                    Chat,
                    (ChatParticipant.chat_id == existing_chat.id)
                    & (Chat.id == existing_chat.id),
                )
                chat_messages = (
                    await session.scalars(chat_messages_select_query)
                ).all()
                chat_participants = (
                    await session.scalars(chat_participants_query)
                ).all()

                chat_participants_read_map = {
                    cp.user_id: ChatParticipantRead(
                        name=cp.name, active=True, typing=False
                    )
                    for cp in chat_participants
                }
                print(chat_messages)
                chat_messages_read = [
                    ChatMessageRead(
                        id=chat_message.id,
                        chat_id=existing_chat.id,
                        message=chat_message.message,
                        timestamp=chat_message.timestamp,
                        sender=chat_participants_read_map[chat_message.sender].name,
                    )
                    for chat_message in chat_messages
                ]

                await self.send_to_websocket(
                    WebsocketSend(
                        chat_id=existing_chat.id,
                        messages=chat_messages_read,
                        participants=list(chat_participants_read_map.values()),
                        me="me",
                    ),
                    websocket,
                )
                await self.add_websocket(
                    websocket, user_id, task_id, component_id, existing_chat.id
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
                    participants=[
                        ChatParticipantRead(name="self", active=True, typing=False)
                    ],
                ),
                websocket,
            )
        await self.add_websocket(
            websocket, user_id, task_id, component_id, pending_chat.id
        )
        return True

    async def add_websocket(
        self,
        websocket: WebSocket,
        user_id: UUID4,
        task_id: UUID4,
        component_id: str,
        chat_id: UUID4,
    ):
        if chat_id not in self.chats:
            self.chats[chat_id] = ChatState(
                task_id=task_id,
                component_id=component_id,
                chat_id=chat_id,
                agents={},  # TODO: init agents by reading task config
            )
        self.chats[chat_id].websockets[user_id] = websocket
        # TODO: update Chat.order

    async def get_current_speaker(self, chat_id: UUID4) -> str:
        # Get the speaker based on the chat order and the chat history
        # Pseudocode:
        # order = get chat order
        # latest_chat_message = get_latest_chat_message
        # order_index = order.index(latest_chat_message.sender)
        # current_order_index = (order_index + 1) % len(order)
        # return order[current_order_index]
        raise NotImplementedError()

    async def receive(self, json: dict, websocket: WebSocket) -> None:
        try:
            data = WebsocketReceive.model_validate(json)
        except ValidationError as e:
            await websocket.send_json(WebsocketSend(error=str(e)))
            return
        chat_id, user_id = await self.get_websocket_chat(websocket)

        logger.debug(f"Websocket for chat {chat_id} user {user_id} received {data}")
        # TODO: check if user is current speaker, if not reject msg
        # if user is current speaker:
        # 1. save message to db
        # 2. determine next speaker
        # 3. send message and speaker info to all participants

        new_chat_message = ChatMessage(
            message=data.message,
            sender=user_id,
            chat_id=chat_id,
        )
        new_chat_message_read = ChatMessageRead(
            id=new_chat_message.id,
            chat_id=chat_id,
            message=new_chat_message.message,
            timestamp=new_chat_message.timestamp,
            sender="self",
        )
        async with get_session() as session:
            session.add(new_chat_message)
            await session.commit()

        await self.send_to_chat(
            WebsocketSend(
                chat_id=chat_id,
                messages=[new_chat_message_read],
            )
        )

    async def send_to_websocket(self, data: WebsocketSend, websocket: WebSocket):
        logger.debug(f"Sending to websocket {websocket} data {data}")
        await websocket.send_text(data.model_dump_json())

    async def send_to_chat(self, data: WebsocketSend) -> None:
        logger.debug(f"Sending to chat {data.chat_id} data {data}")
        data_json = data.model_dump_json()
        futures = [
            ws.send_text(data_json)
            for ws in self.chats[data.chat_id].websockets.values()
        ]
        await asyncio.gather(*futures)

    async def get_websocket_chat(self, websocket: WebSocket) -> tuple[UUID4, UUID4]:
        """
        :returns: chat_id, user_id
        """
        for chat_id, chat in self.chats.items():
            for user_id, ws in chat.websockets.items():
                if ws == websocket:
                    return chat_id, user_id
        raise ValueError("Websocket not found in any chat")

    async def disconnect(self, websocket: WebSocket) -> None:
        await websocket.close()
        chat_id, user_id = await self.get_websocket_chat(websocket)
        del self.chats[chat_id].websockets[user_id]
        await self.send_to_chat(
            WebsocketSend(chat_id=chat_id, error="User disconnected")
        )
