from fastapi import APIRouter, Depends

import services.user
from apis.utils import AUTH_RESPONSES, check_auth
from models.models import NewUser, User

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
    responses=AUTH_RESPONSES,
    dependencies=[Depends(check_auth(True))],
)
async def get_user(user_id: str):
    return await services.user.get_user(user_id)