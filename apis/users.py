from fastapi import APIRouter, HTTPException, status

import services.user
from models.task import Task, TaskRead, TaskResponse
from models.user import User, UserCreate

router = APIRouter(prefix="/users")


CREATE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User email already taken"
)


@router.put(
    "",
    description="Creates a new non-admin user. Requires an admin's user_id for authentication.",
    response_model=User,
)
async def create_user(new_user: UserCreate):
    user = await services.user.create_user(new_user)
    if user is None:
        raise CREATE_USER_EXCEPTION
    return user


@router.get("", response_model=list[User],)
async def get_all_users():
    return await User.all()


GET_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)


@router.get("{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await services.user.get_user(user_id)
    if user is None:
        raise GET_USER_EXCEPTION
    return user


@router.get("/users_responses", response_model=list[TaskResponse])
async def get_all_users_responses():
    return await services.user.get_user_responses()

@router.get("/me/tasks", response_model=list[TaskRead])
async def get_my_tasks():
    all_tasks = await Task.all()
    all_tasks = [*all_tasks, *all_tasks]
    return all_tasks