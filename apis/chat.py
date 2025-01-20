from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

# from apis.utils import NOT_AUTHENTICATED, check_auth
from models.models import LLMInput, LLMResponse
from services.chat import get_llm_response, config_agent
from services.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


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
            logger.info(f'Websocket disconnect: {e}')
            return
        except Exception as e:
            logger.exception(f"Unexpected exception in chat endpoint: {e}")
            response = LLMResponse(
                error=f"An unexpected error occurred: {str(e)}",
                response="",
                agent_data={},
            )
            await ws.send_json(response.model_dump())