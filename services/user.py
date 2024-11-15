import uuid
from typing import List
from sqlalchemy.orm import joinedload

from sqlalchemy import select

from models.database import get_session
from models.models import NewUser, User


async def create_user(new_user: NewUser) -> User:
    user = User(**new_user.model_dump(), user_code=str(uuid.uuid4()))
    async with get_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user

async def get_all_users() -> List[User]:
    async with get_session() as session:
        return list((await session.execute(select(User).options(joinedload(User.tasks)))).scalars())

