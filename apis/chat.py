from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from apis.utils import NOT_AUTHENTICATED, check_auth
from models.models import LLMPrompt, LLMResponse
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
                await check_auth(False)
                response = await get_llm_response(prompt)
            except ValidationError as e:
                response = LLMResponse(error=f'Request validation error: {e}')
            except HTTPException:
                response = LLMResponse(error=NOT_AUTHENTICATED)
            await ws.send_json(response.model_dump())
    except WebSocketDisconnect:
        ...
