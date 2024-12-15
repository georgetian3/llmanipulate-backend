from fastapi import APIRouter, Depends

import services.user
from apis.utils import AUTH_RESPONSES, HTTP_400_EXCEPTION, NOT_FOUND_HTTP_EXCEPTION, check_auth, create_error_response
from models.models import NewUser, User


user_router = APIRouter()


@user_router.put(
    "/users",
    description="Creates a new non-admin user. Requires an admin's user_id for authentication.",
    response_model=User,
    responses=AUTH_RESPONSES | create_error_response(HTTP_400_EXCEPTION),
    dependencies=[Depends(check_auth(True))],
)
async def create_user(new_user: NewUser):
    user = await services.user.create_user(new_user)
    if user is None:
        raise HTTP_400_EXCEPTION
    return user


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
    responses=AUTH_RESPONSES | create_error_response(NOT_FOUND_HTTP_EXCEPTION),
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
