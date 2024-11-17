from fastapi import APIRouter

import services.user
from models.models import NewUser, User

user_router = APIRouter()


@user_router.post("/create_user", response_model=User)
async def create_user(new_user: NewUser):
    user = await services.user.create_user(new_user)
    return user

@user_router.get("/get_all_users", response_model=list[User])
async def get_all_users():
    return await services.user.get_all_users()

