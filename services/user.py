import uuid
from typing import List

from sqlalchemy import select

from models.models import NewUser, User
from services.base import BaseService


class UserService(BaseService):
    async def create_user(self, new_user: NewUser) -> User:
        user = User(**new_user.model_dump(), user_code=str(uuid.uuid4()))
        async with self._database.get_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    async def get_all_users(self) -> List[User]:
        async with self._database.get_session() as session:
            return list((await session.execute(select(User))).scalars())
