from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from models.models import LLMPrompt
from services.chat import get_llm_response

chat_router = APIRouter()


@chat_router.websocket("/chat")
async def chat_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            prompt = await ws.receive_json()
            try:
                prompt = LLMPrompt.model_validate_json(prompt)
            except ValidationError as e:
                await ws.send_json(e.__dict__)
                continue
            response = await get_llm_response(prompt)
            await ws.send_json(response.model_dump())
    except WebSocketDisconnect:
        print("Disconnected")
