import datetime

from models.database import get_session
from models.models import Response
from services.agent import Agent
from datetime import datetime



async def create_response(user_id,task_id) -> id:
    try:
        response = Response(user_id=user_id, task_id=task_id, time_created=datetime.now())
        async with get_session() as session:
            session.add(response)

            await session.commit()

            await session.refresh(response)

        return response.id
    except Exception as e:
        print(f"Error saving response to database: {e}")
        return None

async def save_response(agent: Agent, response_id: int) -> bool:
    async with get_session() as session:
        conv_history = {str(i + 1): message for i, message in enumerate(agent.messages[1:])}

        existing_response = await session.get(Response, response_id)

        if existing_response:
            existing_response.conv_history = conv_history
            session.add(existing_response)
        else:
            raise ValueError(f"Response with ID {response_id} not found.")

        await session.commit()

        await session.refresh(existing_response)

    return True