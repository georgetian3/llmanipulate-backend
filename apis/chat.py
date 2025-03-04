from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import uuid
import asyncio

chat_router = APIRouter()

# Dictionary to store rooms and their connections
rooms: Dict[str, List[WebSocket]] = {}
users: Dict[str, Dict[WebSocket, str]] = {}  # Stores users by room

@chat_router.post("/create_room")
def create_room():
    """Creates a new chat room and returns its ID."""
    room_id = str(uuid.uuid4())  # Generate a unique identifier
    rooms[room_id] = []  # Initialize the room
    users[room_id] = {}  # Initialize the users in the room
    return {"room_id": room_id}

@chat_router.websocket("/join/{room_id}/{username}")
async def join_room(websocket: WebSocket, room_id: str, username: str):
    """Handles WebSocket connections for users joining a room."""
    if room_id not in rooms:
        await websocket.close(code=1008, reason="Room not found")
        return

    await websocket.accept()
    rooms[room_id].append(websocket)
    users[room_id][websocket] = username  # Store the user's name

    try:
        while True:
            data = await websocket.receive_text()
            sender_name = users[room_id].get(websocket, "Unknown")
            message = {"user": sender_name, "message": data}

            # Send the message to ALL users in the room, including the sender
            for ws in rooms[room_id]:
                await ws.send_json(message)

    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        del users[room_id][websocket]
        if not rooms[room_id]:
            del rooms[room_id]  # Remove the room if it's empty
            del users[room_id]