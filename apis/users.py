from fastapi import APIRouter, HTTPException, status

import services.user
from models.response import Response
from models.user import User, UserCreate

router = APIRouter()


CREATE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User email already taken"
)


@router.put(
    "/users",
    description="Creates a new non-admin user. Requires an admin's user_id for authentication.",
    response_model=User,
)
async def create_user(new_user: UserCreate):
    user = await services.user.create_user(new_user)
    if user is None:
        raise CREATE_USER_EXCEPTION
    return user


@router.get(
    "/users",
    response_model=list[User],
)
async def get_all_users():
    return await services.user.get_all_users()


GET_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)


@router.get(
    "/users/{user_id}",
    response_model=User,
)
async def get_user(user_id: str):
    user = await services.user.get_user(user_id)
    if user is None:
        raise GET_USER_EXCEPTION
    return user


@router.get("/users_responses", response_model=list[Response])
async def get_all_users_responses():
    return await services.user.get_user_responses()
