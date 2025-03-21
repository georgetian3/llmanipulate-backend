from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import UUID4

from models.chat import (
    ChatMessageRead,
    WebsocketReceive,
    WebsocketSend,
)
from services.chat import WebsocketManager
from services.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat")

manager = WebsocketManager()


@router.websocket("")
async def chat(websocket: WebSocket, user: UUID4, task: UUID4, component: str):
    connected = await manager.connect(
        websocket, user_id=user, task_id=task, component_id=component
    )
    if not connected:
        return
    try:
        while True:
            await manager.receive(await websocket.receive_json(), websocket)
    except Exception:
        logger.exception("Chat websocket exception")
        await manager.disconnect(websocket)


###############################################################################
# These endpoints are used for generating OpenAPI client code


@router.get("/example/send")
async def example_send(_: WebsocketSend): ...


@router.get("/example/receive")
async def example_receive(_: WebsocketReceive): ...


@router.get("/example/chat-message-read")
async def example_chat_message_read(_: ChatMessageRead): ...


###############################################################################


# def config_agent(agent_name: str) -> BaseAgent:
#     agent = OpenAIAgent()
#     model_name = "gpt-4o-mini"
#     agent.set_attributes(model_name, agent_name)
#     agent.fill_prompt()
#     return agent


# # ✅ In-memory storage
# rooms: Dict[str, List[WebSocket]] = {}
# users: Dict[str, Dict[WebSocket, Dict[str, Union[str, bool]]]] = {}
# agents: Dict[str, Dict[str, BaseAgent]] = {}
# room_configs: Dict[str, Dict[str, Union[bool, List[str], int, str]]] = {}


# class RoomConfig(BaseModel):
#     """✅ Schema for creating a chat room."""

#     all_users: bool = Field(..., example=True)
#     order: List[str] = Field(
#         default=[], examples=[["/agent1", "human", "/agent2", "human", "/agent3"]]
#     )


# @router.post("/create_room")
# async def create_room(
#     room_data: RoomConfig, session: AsyncSession = Depends(get_async_session)
# ):
#     """✅ Creates a chat room and sets the first speaker for turn-based mode."""
#     room_id = str(uuid.uuid4())
#     rooms[room_id] = []
#     users[room_id] = {}
#     agents[room_id] = {}

#     turn_index = 0

#     # store config
#     room_configs[room_id] = {
#         "all_users": room_data.all_users,
#         "order": [str(participant) for participant in room_data.order],
#         "turn_index": turn_index,
#         "current_speaker": None,  # no speaker yet
#         "room_ready": False,  # not ready until humans join
#         "last_human": None,  # track last human ID for round-robin
#     }

#     # create an empty ChatHistory DB row
#     async with session.begin():
#         chat_history = Chat(id=room_id)
#         session.add(chat_history)

#     agents_list = [p for p in room_data.order if p.startswith("/agent")]
#     for agent in agents_list:
#         new_agent = config_agent(agent)
#         agents[room_id][agent] = new_agent

#     return {"room_id": room_id}


# async def notify_turn_change(room_id: str):
#     """✅ Sends a turn change notification to all users in the room."""
#     config = room_configs.get(room_id, {})
#     next_speaker = config.get("current_speaker")

#     active_sockets = [
#         ws
#         for ws in rooms.get(room_id, [])
#         if ws.application_state == WebSocketState.CONNECTED
#     ]
#     if not active_sockets:
#         print(f"⚠️ No active connections in room {room_id}, skipping turn update.")
#         return

#     for ws in active_sockets:
#         try:
#             await ws.send_json({"type": "TURN_CHANGE", "current_speaker": next_speaker})
#         except Exception as e:
#             print(f"⚠️ Error sending turn change: {e}")
#             rooms[room_id].remove(ws)


# async def generate_message(room_id: str, agent: str) -> str:
#     """🤖 Simulates an agent generating a message (replace with AI logic)."""
#     print(f"🤖 {agent} is thinking...")

#     response = agents[room_id][agent].generate()
#     # ...some real LLM call or internal logic...
#     return response["content"]


# async def get_next_human(room_id: str) -> Union[str, None]:
#     """Finds the next available human user in a round-robin way."""
#     config = room_configs.get(room_id, {})
#     human_users = [
#         user_data["id"]
#         for ws, user_data in users[room_id].items()
#         if not user_data["id"].startswith("/agent")  # i.e., real user UUID
#     ]

#     if not human_users:
#         return None  # no humans found

#     last_human = config.get("last_human", None)
#     if last_human and last_human in human_users:
#         last_index = human_users.index(last_human)
#         next_index = (last_index + 1) % len(human_users)
#         next_human = human_users[next_index]
#     else:
#         next_human = human_users[0]

#     config["last_human"] = next_human
#     return next_human


# async def process_turn(room_id: str, session: AsyncSession, advance: bool = True):
#     """Handles turn-based chat logic, ensuring turns rotate correctly."""
#     config = room_configs.get(room_id, {})
#     order = config.get("order", [])

#     # if room isn't ready or no valid order, just skip
#     if not order or not config.get("room_ready", False):
#         print(f"⚠️ Room {room_id} not ready or empty order, skipping.")
#         return

#     # move to next index
#     if advance:
#         config["turn_index"] = (config["turn_index"] + 1) % len(order)

#     next_speaker = order[config["turn_index"]]
#     print(f"\n🔄 Next turn: {next_speaker}")

#     # If 'human', pick the next actual user from round-robin
#     if next_speaker == "human":
#         real_user_uuid = await get_next_human(room_id)
#         if not real_user_uuid:
#             print("⚠️ No humans found to assign turn.")
#             return
#         print(f"👤 Assigning turn to: {real_user_uuid}")
#         next_speaker = real_user_uuid

#     config["current_speaker"] = next_speaker

#     # If it's an agent, we handle the message generation immediately
#     if next_speaker.startswith("/agent"):
#         agent_message = await generate_message(room_id, next_speaker)

#         # update other agents messages
#         for agent in agents[room_id]:
#             if agent != next_speaker:
#                 agent = agents[room_id][agent]
#                 agent.add_message({"role": "assistant", "content": agent_message})

#         # store in DB
#         async with session.begin():
#             chat_message = ChatMessage(
#                 chat_id=room_id,
#                 sender_agent=next_speaker,
#                 message=agent_message,
#                 timestamp=datetime.utcnow(),
#             )
#             session.add(chat_message)
#             await session.flush()

#             # broadcast the agent's message
#             message_json = {
#                 "user": next_speaker,
#                 "message": agent_message,
#                 "timestamp": chat_message.timestamp.isoformat(),
#             }
#             for ws in rooms[room_id]:
#                 await ws.send_json(message_json)

#         # Then automatically queue up the next turn
#         asyncio.create_task(process_turn(room_id, session))

#     # notify all clients about who can speak now
#     await notify_turn_change(room_id)


# @router.websocket("/join/{room_id}/{user_id}")
# async def join_room(
#     websocket: WebSocket,
#     room_id: str,
#     user_id: UUID4,
#     session: AsyncSession = Depends(get_async_session),
# ):
#     """✅ Handles WebSocket connections and ensures turn-based logic works."""
#     if room_id not in rooms:
#         await websocket.close(code=1008, reason="Room not found")
#         return

#     await websocket.accept()
#     rooms[room_id].append(websocket)
#     users[room_id][websocket] = {"id": str(user_id), "can_speak": True}

#     # Mark room as ready if we have enough humans
#     config = room_configs.get(room_id, {})
#     human_users = [
#         ud["id"]
#         for _, ud in users[room_id].items()
#         if not ud["id"].startswith("/agent")
#     ]
#     expected_human_count = sum(1 for p in config["order"] if p == "human")

#     if len(human_users) >= expected_human_count:
#         print("✅ All humans joined, starting conversation!")
#         config["room_ready"] = True

#         # If first speaker not set, set it to the "order[0]"
#         if config["current_speaker"] is None:
#             config["current_speaker"] = config["order"][config["turn_index"]]
#         if config["current_speaker"].startswith("/agent"):
#             await process_turn(room_id, session, advance=False)
#         else:
#             await notify_turn_change(room_id)

#     try:
#         while True:
#             # Wait for a message from the user
#             data = await websocket.receive_text()
#             sender_id = users[room_id][websocket]["id"]

#             # Check turn ownership
#             if sender_id != config.get("current_speaker"):
#                 await websocket.send_json(
#                     {"type": "ERROR", "message": "⏳ Wait for your turn!"}
#                 )
#                 continue

#             # update agents messages
#             for agent in agents[room_id]:
#                 agents[room_id][agent].add_message(
#                     {"role": "user", "content": f"User-{sender_id}: {data}"}
#                 )

#             # Store user message
#             async with session.begin():
#                 chat_message = ChatMessage(
#                     chat_id=room_id,
#                     sender_uuid=uuid.UUID(sender_id),
#                     message=data,
#                     timestamp=datetime.utcnow(),
#                 )
#                 session.add(chat_message)
#                 await session.flush()
#                 timestamp_str = chat_message.timestamp.isoformat()

#             # Broadcast user message
#             message_json = {
#                 "user": sender_id,
#                 "message": data,
#                 "timestamp": timestamp_str,
#             }
#             for ws in rooms[room_id]:
#                 await ws.send_json(message_json)

#             # Once user has spoken, move to next turn
#             await process_turn(room_id, session)

#     except WebSocketDisconnect:
#         rooms[room_id].remove(websocket)
#         del users[room_id][websocket]
#         if not rooms[room_id]:
#             # no one left in this room, cleanup
#             del rooms[room_id]
#             del users[room_id]
#             del room_configs[room_id]
#         print(f"🚪 User {user_id} left the chat.")
