from models.database import get_session
from models.models import Response


async def create_response(response: Response) -> bool:
    # TODO: save response to db
    async with get_session() as session:
        session.add(response)
        await session.commit()
    return True
