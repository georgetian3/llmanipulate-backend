

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.chat import get_llm_response


chat_router = APIRouter()

@chat_router.websocket("/chat")
async def chat_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            prompt = await ws.receive_json()
            response = await get_llm_response(prompt)
            await ws.send_json(response.model_dump())
    except WebSocketDisconnect:
        print('Disconnected')