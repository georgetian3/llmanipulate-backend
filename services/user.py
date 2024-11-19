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


# async def create_user(new_user: NewUser) -> User:
#     user = User(
#         **new_user.model_dump(),
#         user_code=str(uuid.uuid4()),
#         password_hash=hash_password(new_user.password)
#     )
#     async with get_session() as session:
#         session.add(user)
#         await session.commit()
#         await session.refresh(user)
#     return user


# async def get_all_users() -> list[User]:
#     async with get_session() as session:
#         return list(
#             (
#                 await session.execute(select(User).options(joinedload(User.tasks)))
#             ).scalars()
#         )
