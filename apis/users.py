from fastapi import APIRouter, Depends, status

import services.user
from apis.utils import ALL_RESPONSES, AUTH_RESPONSES, NOT_FOUND_HTTP_EXCEPTION, check_auth
from models.models import ErrorResponse, NewUser, User, PartialUser


user_router = APIRouter()


@user_router.put(
    "/users",
    description="Creates a new non-admin user. Requires an admin's user_id for authentication.",
    response_model=User,
    responses=AUTH_RESPONSES,
    dependencies=[Depends(check_auth(True))],
)
async def create_user(new_user: NewUser):
    return await services.user.create_user(new_user)


@user_router.get(
    "/users",
    response_model=list[User],
    responses=AUTH_RESPONSES,
    dependencies=[Depends(check_auth(True))],
)
async def get_all_users():
    return await services.user.get_all_users()

@user_router.get(
    "/users/{user_id}",
    response_model=User,
    responses=ALL_RESPONSES,
)
async def get_user(user_id: str):
    user = await services.user.get_user(user_id)
    if user is None:
        raise NOT_FOUND_HTTP_EXCEPTION
    return user

@user_router.get(
    "/users_responses",
    responses=AUTH_RESPONSES,
    dependencies=[Depends(check_auth(True))],
)
async def get_all_users_responses():
    return await services.user.get_user_responses()