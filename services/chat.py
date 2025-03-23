import asyncio
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from fastapi import WebSocket
from pydantic import UUID4, ValidationError
from sqlalchemy import func, insert, null, select, text, update
from sqlalchemy.exc import DBAPIError

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
from models.task_config.agent import AgentConfig
from models.task_config.chat import ChatConfig
from models.task_participant import TaskParticipant
from services.agents.base_agent import BaseAgent
from services.logging import get_logger

logger = get_logger(__name__)


def occurence_index(l: list, elem: Any, n: int) -> int:
    """
    Gives the index of the `n`th occurence of `elem` in `l`, raises `ValueError` if the `n`th occurence doesn't exist
    """
    if n <= 0:
        raise ValueError("`n` must be positive")
    if n > len(l):
        ValueError("n > len(l)")
    count = 0
    for i, e in enumerate(l):
        if e == elem:
            count += 1
            if count == n:
                return i
    raise ValueError("`n`th occurance not found")


@dataclass
class ChatState:
    chat_id: UUID4
    task: Task
    component_id: str
    # map of user id to websocket
    websockets: dict[UUID4, WebSocket] = field(default_factory=dict)
    # map of agent ID (from agent config) to agent instance
    agents: dict[str, BaseAgent] = field(default_factory=dict)


class WebsocketManager:
    def __init__(self):
        self.chats: dict[UUID4, ChatState] = {}

    async def check_user_task_permissions(
        self, user_id: UUID4, task_id: UUID4, component_id: str
    ) -> Task | None:
        task_query = (
            select(Task)
            .join(
                TaskParticipant,
                Task.id == TaskParticipant.task_id,
            )
            .where(Task.id == task_id, TaskParticipant.user_id == user_id)
        )
        async with get_session() as session:
            task = await session.scalar(task_query)

        if not task:
            logger.debug(
                f"Task {task_id} does not exist or user {user_id} is not a participant"
            )
            return
        task.parse_config()
        if component_id not in task.config.component_map:
            logger.warning(
                f"Component {component_id} does not exist for task {task_id}"
            )
            return
        return task

    async def get_chat_history(
        self, chat_id: UUID4
    ) -> tuple[list[ChatMessageRead], list[ChatParticipantRead]]:
        chat_messages_select_query = select(ChatMessage).where(
            ChatMessage.chat_id == chat_id
        )
        chat_participants_query = select(ChatParticipant).join(
            Chat,
            (ChatParticipant.chat_id == chat_id) & (Chat.id == chat_id),
        )
        async with get_session() as session:
            chat_messages = (await session.scalars(chat_messages_select_query)).all()
            chat_participants = (await session.scalars(chat_participants_query)).all()

        chat_participants_read_map = {
            (cp.user_id, cp.agent_id): ChatParticipantRead(
                name=cp.name, active=True, typing=False
            )
            for cp in chat_participants
        }
        chat_messages_read = sorted(
            [
                ChatMessageRead(
                    id=chat_message.id,
                    chat_id=chat_id,
                    message=chat_message.message,
                    timestamp=chat_message.timestamp,
                    sender=chat_participants_read_map[
                        (chat_message.user_id, chat_message.agent_id)
                    ].name,
                )
                for chat_message in chat_messages
            ],
            key=lambda x: x.timestamp,
        )
        return chat_messages_read, chat_participants_read_map.values()

    async def handle_existing_chat(
        self, user_id: UUID4, task: Task, chat: Chat, websocket: WebSocket
    ) -> None:
        await self.add_websocket(websocket, user_id, task, chat.component_id, chat.id)
        chat_messages_read, chat_participants_read = await self.get_chat_history(
            chat.id
        )
        me_query = select(ChatParticipant).where(
            ChatParticipant.user_id == user_id, ChatParticipant.chat_id == chat.id
        )
        async with get_session() as session:
            cp = await session.scalar(me_query)
        await self.send_to_websocket(
            WebsocketSend(
                chat_id=chat.id,
                messages=chat_messages_read,
                participants=chat_participants_read,
                me=cp.name,
            ),
            websocket,
        )

    async def join_new_chat(
        self, user_id: UUID4, task: Task, chat_config: ChatConfig, websocket: WebSocket
    ):
        if chat_config.humans_required is None:  # task-wide chat, only one should exist
            pending_chat_select_query = (
                select(Chat)
                .where(Chat.task_id == task.id, Chat.component_id == chat_config.id)
                .limit(1)
            )
        else:
            pending_chat_select_query = (
                select(Chat)
                .join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
                .group_by(Chat.id)
                .having(
                    func.count(ChatParticipant.user_id)
                    < (chat_config.humans_required + len(chat_config.agents))
                )
                .limit(1)
            )
        async with get_session() as session:
            vacant_chat: Chat | None = (
                await session.execute(pending_chat_select_query)
            ).scalar_one_or_none()
            if vacant_chat:
                logger.debug(f"Found vacant chat {vacant_chat.id}")
            else:
                logger.debug("No vacant chats, creating new chat")
                vacant_chat = Chat(task_id=task.id, component_id=chat_config.id)
                session.add(vacant_chat)
                # Add agents as chat participants at the creation of every new chat
                session.add_all(
                    ChatParticipant(
                        name=agent.display_name
                        if agent.display_name
                        else f"Participant {chat_config.order.index(agent.id) + 1}",
                        agent_id=agent.id,
                        chat_id=vacant_chat.id,
                        order=chat_config.order.index(agent.id),
                    )
                    for agent in chat_config.agents
                )
                await session.commit()
                await session.refresh(vacant_chat)
            chat_id = vacant_chat.id


        # get the smallest number that does not exist in order, i.e. fill in the order gaps
        stmt = text(f"""
            SELECT MIN(t1.order + 1)
            FROM {ChatParticipant.__tablename__} t1
            LEFT JOIN {ChatParticipant.__tablename__} t2
            ON t1.order + 1 = t2.order
            WHERE t1.chat_id = :chat_id
            AND t2.chat_id = :chat_id
            AND t2.order IS NULL
        """)

        async with get_session() as session:
            missing_order = await session.scalar(stmt, {"chat_id": chat_id})
            next_order = 0 if missing_order is None else missing_order
            logger.debug(f"next order {next_order}")
            new_name = f"Participant {occurence_index(chat_config.order, 'human', next_order + 1) + 1}"
            logger.debug(f"Name: {new_name}")
            new_participant = ChatParticipant(
                name=new_name,
                user_id=user_id,
                chat_id=chat_id,
                order=next_order,
            )
            session.add(new_participant)
            await session.commit()

        await self.send_to_websocket(
            WebsocketSend(
                chat_id=chat_id,
                messages=[],
                participants=[
                    ChatParticipantRead(
                        name=new_name, active=True, typing=False
                    )
                ],
                me=new_name,
            ),
            websocket,
        )
        await self.add_websocket(websocket, user_id, task, chat_config.id, chat_id)

    async def connect(
        self, websocket: WebSocket, user_id: UUID4, task_id: UUID4, component_id: str
    ) -> bool:
        logger.debug(
            f"Websocket connect user_id={user_id} task_id={task_id} component_id={component_id}"
        )
        task = await self.check_user_task_permissions(user_id, task_id, component_id)
        if not task:
            await websocket.close()
            return False

        # user allowed to chat
        await websocket.accept()

        async def _serializable_db_actions():
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
                existing_chat = await session.scalar(existing_chat_select_query)
            if existing_chat:
                # already participant of a chat, send existing chat messages
                logger.debug(
                    f"User {user_id} already participant in chat {existing_chat.id}"
                )
                await self.handle_existing_chat(user_id, task, existing_chat, websocket)
            else:
                # user not part of a chat, create new chat
                logger.debug("User currently not in a chat")
                await self.join_new_chat(
                    user_id, task, task.config.component_map[component_id], websocket
                )
        # the loop below is needed to catch exceptions raised due to postgres' transaction isolation level being set to serializable
        # it has been recommended to retry the operation if it errors
        # see https://www.postgresql.org/docs/current/transaction-iso.html
        count = 0
        while True:
            count += 1
            logger.debug(f"Serializable loop count: {count}")
            try:
                await _serializable_db_actions()
                break
            except DBAPIError:
                continue

        return True

    async def add_websocket(
        self,
        websocket: WebSocket,
        user_id: UUID4,
        task: Task,
        component_id: str,
        chat_id: UUID4,
    ):
        if chat_id not in self.chats:
            agents: list[AgentConfig] = task.config.component_map[component_id].agents
            order = task.config.component_map[component_id].order
            self.chats[chat_id] = ChatState(
                task=task,
                component_id=component_id,
                chat_id=chat_id,
                agents={agent.id: agent.create() for agent in agents},
            )
        self.chats[chat_id].websockets[user_id] = websocket

    async def receive(self, json: dict, websocket: WebSocket) -> None:
        try:
            data = WebsocketReceive.model_validate(json)
        except ValidationError as e:
            await websocket.send_json(WebsocketSend(error=str(e)))
            return

        if data.message is None:
            return
        chat_state, user_id = await self.get_websocket_context(websocket)
        logger.debug(
            f"Websocket for chat {chat_state.chat_id} user {user_id} received {data}"
        )
        human_chat_message = ChatMessage(
            message=data.message,
            chat_id=chat_state.chat_id,
            user_id=user_id,
        )
        participant_count = len(
            chat_state.task.config.component_map[chat_state.component_id].order
        )
        insert_message_query = text(f"""
            WITH check_participant AS (
                SELECT 1
                FROM {ChatParticipant.__tablename__} cp
                JOIN chat c ON c.id = cp.chat_id
                WHERE cp.chat_id = :chat_id
                AND cp.user_id = :user_id
                AND cp."order" = c."order"
            ),
            update_chat AS (
                UPDATE {Chat.__tablename__}
                SET "order" = ("order" + 1) % {participant_count}
                WHERE id = :chat_id
                AND EXISTS (SELECT 1 FROM check_participant)
                RETURNING id
            )
            INSERT INTO {ChatMessage.__tablename__} (id, chat_id, user_id, agent_id, message, timestamp)
            SELECT :id, :chat_id, :user_id, :agent_id, :message, :timestamp
            WHERE EXISTS (SELECT 1 FROM update_chat)
            RETURNING id;
        """)
        select_chat_participant_query = select(ChatParticipant).where(
            ChatParticipant.chat_id == chat_state.chat_id,
            ChatParticipant.user_id == user_id,
        )
        async with get_session() as session:
            human_cp = await session.scalar(select_chat_participant_query)
            result = await session.scalar(
                insert_message_query, human_chat_message.model_dump()
            )
            await session.commit()
            await session.refresh(human_cp)
        if not result:
            await self.send_to_websocket(
                WebsocketSend(error="Not your turn"), websocket
            )
            return

        await self.send_to_chat(
            WebsocketSend(
                chat_id=chat_state.chat_id,
                messages=[
                    ChatMessageRead(
                        id=human_chat_message.id,
                        chat_id=chat_state.chat_id,
                        message=human_chat_message.message,
                        timestamp=human_chat_message.timestamp,
                        sender=human_cp.name,
                    )
                ],
            )
        )

        chat = await Chat.get(chat_state.chat_id)
        current_speaker_query = (
            select(ChatParticipant)
            .join(Chat, Chat.id == ChatParticipant.chat_id)
            .where(ChatParticipant.order == Chat.order, ChatParticipant.agent_id != "")
        )
        async with get_session() as session:
            agent_cp = await session.scalar(current_speaker_query)

        if not agent_cp:
            return

        agent = chat_state.agents[agent_cp.agent_id]
        chat_history, _ = await self.get_chat_history(chat.id)
        agent.set_chat_history(chat_history)
        response = await agent.get_response()
        agent_chat_message = ChatMessage(
            message=response,
            chat_id=chat_state.chat_id,
            agent_id=agent_cp.agent_id,
        )
        await agent_chat_message.save()
        increment_order_query = (
            update(Chat)
            .where(Chat.id == chat_state.chat_id)
            .values(order=(Chat.order + 1) % participant_count)
        )
        async with get_session() as session:
            await session.execute(increment_order_query)
            await session.commit()

        await self.send_to_chat(
            WebsocketSend(
                chat_id=chat_state.chat_id,
                messages=[
                    ChatMessageRead(
                        id=agent_chat_message.id,
                        chat_id=chat_state.chat_id,
                        message=agent_chat_message.message,
                        timestamp=agent_chat_message.timestamp,
                        sender=agent_cp.name,
                    )
                ],
            )
        )

    async def send_to_websocket(self, data: WebsocketSend, websocket: WebSocket):
        logger.debug(f"Sending to websocket {websocket}")
        await websocket.send_text(data.model_dump_json())

    async def send_to_chat(self, data: WebsocketSend) -> None:
        logger.debug(f"Sending to chat {data.chat_id}")
        data_json = data.model_dump_json()
        futures = [
            ws.send_text(data_json)
            for ws in self.chats[data.chat_id].websockets.values()
        ]
        await asyncio.gather(*futures)

    async def get_websocket_context(
        self, websocket: WebSocket
    ) -> tuple[ChatState, UUID4]:
        for chat in self.chats.values():
            for user_id, ws in chat.websockets.items():
                if ws == websocket:
                    return chat, user_id
        raise ValueError("Websocket not found in any chat")

    async def disconnect(self, websocket: WebSocket) -> None:
        try:
            await websocket.close()
        except:
            ...
        chat_state, user_id = await self.get_websocket_context(websocket)
        logger.info(
            f"Websocket disconnected for chat {chat_state.chat_id} user {user_id}"
        )
        del chat_state.websockets[user_id]
        await self.send_to_chat(
            WebsocketSend(chat_id=chat_state.chat_id, error="User disconnected")
        )

    async def on_task_delete(self) -> None:
        raise NotImplementedError()

    async def on_user_delete(self) -> None:
        raise NotImplementedError()
