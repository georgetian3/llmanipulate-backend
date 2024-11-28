from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

# from apis.utils import NOT_AUTHENTICATED, check_auth
from models.models import LLMInput, LLMResponse
from services.chat import get_llm_response, config_agent
from services.responses import create_response


chat_router = APIRouter()


@chat_router.websocket("/chat")
async def chat_endpoint(ws: WebSocket):
    await ws.accept()

    agent = None
    response_id = None

    try:
        while True:
            try:
                data = await ws.receive_json()

                if agent is None:
                    # Initialize agent only once on the first message
                    llm_input = LLMInput(**data)
                    agent = await config_agent(llm_input)
                    response_id = await create_response(llm_input.user_id, llm_input.task_id)

                else:
                    # Parse subsequent messages without reinitializing the agent
                    llm_input = LLMInput(**data)

                response = await get_llm_response(llm_input, agent, response_id)

            except ValidationError as e:
                response = LLMResponse(error=f"Request validation error: {str(e)}", response="")
            except Exception as e:
                response = LLMResponse(error=f"An unexpected error occurred: {str(e)}", response="")

            await ws.send_json(response.model_dump())

    except WebSocketDisconnect:
        print("WebSocket disconnected")


        # Old Code
        """@chat_router.websocket("/chat")
        async def chat_endpoint(ws: WebSocket):
            await ws.accept()
            try:
                while True:
                    llm_input = await ws.receive_json()
                    try:
                        prompt = LLMInput.model_validate_json(prompt)
                        # await check_auth(False)
                        response = await get_llm_response(prompt)
                    except ValidationError as e:
                        response = LLMResponse(error=f'Request validation error: {e}')
                    # except HTTPException:
                        # response = LLMResponse(error=NOT_AUTHENTICATED)
                    await ws.send_json(response.model_dump())
            except WebSocketDisconnect:
                ..."""

