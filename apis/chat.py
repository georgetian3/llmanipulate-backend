from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from models.models import ChatHistory, LLMInput, LLMResponse
from models.task_config.examples import sample_chat_history
from services.chat import config_agent, get_llm_response
from services.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/chat/{id}", response_model=ChatHistory)
async def get_chat(id: str):
    return sample_chat_history


@router.websocket("/chat")
async def chat_endpoint(ws: WebSocket):
    await ws.accept()

    agent = None

    while True:
        try:
            data = await ws.receive_json()
            if agent is None:
                # Initialize agent only once on the first message
                llm_input = LLMInput(**data)
                agent = await config_agent(llm_input)
            else:
                # Parse subsequent messages without reinitializing the agent
                llm_input = LLMInput(**data)

            response = await get_llm_response(llm_input, agent)
            await ws.send_json(response.model_dump())

        except ValidationError as e:
            logger.exception(f"Unexpected validation error in chat endpoint: {e}")
            response = LLMResponse(
                error=f"Request validation error: {str(e)}",
                response="",
                agent_data={},
            )
            await ws.send_json(response.model_dump())
        except WebSocketDisconnect as e:
            logger.info(f"Websocket disconnect: {e}")
            return
        except Exception as e:
            logger.exception(f"Unexpected exception in chat endpoint: {e}")
            response = LLMResponse(
                error=f"An unexpected error occurred: {str(e)}",
                response="",
                agent_data={},
            )
            await ws.send_json(response.model_dump())
