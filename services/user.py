import uuid

from argon2 import PasswordHasher
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.database import get_session
from models.models import NewUser, User

# _ph = PasswordHasher()


# def hash_password(password: str) -> str:
#     return _ph.hash(password)


# def verify_password(password: str, hash: str) -> bool:
#     try:
#         return _ph.verify(hash, password)
#     except:
#         return False


async def create_user(new_user: NewUser) -> User:
    # TODO: clarify user creation process
    # check if creator is admin before creating
    user = User(
        **new_user.model_dump(),
        id=str(uuid.uuid4()),
    )
    async with get_session() as session:
        session.add(user)
        await session.commit()
    return user


# async def get_all_users() -> list[User]:
#     async with get_session() as session:
#         return list(
#             (
#                 await session.execute(select(User).options(joinedload(User.tasks)))
#             ).scalars()
#         )
