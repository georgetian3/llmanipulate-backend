from fastapi import APIRouter, Depends

import services.user
from apis.utils import AUTH_RESPONSES, auth_required
from models.models import NewUser, User

user_router = APIRouter()


@user_router.put(
    "/user",
    response_model=User,
    responses=AUTH_RESPONSES,
    dependencies=[Depends(auth_required(True))],
)
async def create_user(new_user: NewUser):
    return await services.user.create_user(new_user)


@user_router.get(
    "/users",
    response_model=list[User],
    responses=AUTH_RESPONSES,
    dependencies=[Depends(auth_required(True))],
)
async def get_all_users():
    return await services.user.get_all_users()
