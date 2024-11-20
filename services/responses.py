from sqlalchemy import select
from models.database import get_session
from models.models import Response


async def create_response(response: Response) -> bool:
    # TODO: save response to db
    async with get_session() as session:
        session.add(response)
        await session.commit()
    return True

async def get_responses() -> list[Response]:
    async with get_session() as session:
        return list((await session.execute(select(Response))).scalars())