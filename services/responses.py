import datetime

from sqlalchemy.future import select

from models.database import get_session
from models.models import Response, NewResponse
from datetime import datetime



async def create_response(response: NewResponse) -> Response:
    try:
        print("Request Data Received: 2,3", response.dict())
        response = Response(
            user_id=response.user_id,
            task_name=response.task_name,
            initial_scores=response.initial_scores,
            conv_history=response.conv_history,
            final_scores=response.final_scores,
            time_created=datetime.utcnow()
        )
        async with get_session() as session:
            session.add(response)
            await session.commit()
            await session.refresh(response)
        print("Response saved to database:", response.dict())
        return response

    except Exception as e:
        print(f"Error saving response to database: {e}")
        return None


async def get_responses_by_users(user_id: str):
    async with get_session() as session:
        try:
            # Use select() for querying in async mode
            stmt = select(Response).where(Response.user_id == user_id)
            result = await session.execute(stmt)
            responses = result.scalars().all()

            if not responses:
                return {"error": "No responses found for the given user_id"}

            # Return the responses as a list of dictionaries
            return responses

        except Exception as e:
            return {"error": f"Error fetching responses from database: {str(e)}"}
          
async def get_responses():
    async with get_session() as session:
        try:
            stmt = select(Response)
            result = await session.execute(stmt)
            responses = result.scalars().all()

            if not responses:
                return {"error": "No responses found"}

            return responses

        except Exception as e:
            return {"error": f"Error fetching responses from database: {str(e)}"}