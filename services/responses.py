from datetime import datetime
import pytz
from sqlalchemy import select
from models.database import get_session
from models.models import NewResponse, Response


async def create_response(user_id: str, new_response: NewResponse) -> bool:
    response = Response(
        **new_response.model_dump(),
        user_id=user_id,
        time_created=datetime.now(pytz.UTC)
    )
    async with get_session() as session:
        session.add(response)
        await session.commit()
        await session.refresh(response)
    return response

async def get_responses() -> list[Response]:
    async with get_session() as session:
        return list((await session.execute(select(Response))).scalars())