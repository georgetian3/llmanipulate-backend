from fastapi import APIRouter, Depends, HTTPException, status

import services.user
from models.task import MyTasks, Task, TaskRead, TaskResponse
from models.user import User, UserCreate, UserID
from services.tasks import get_user_tasks
from services.user import current_active_user

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


@router.get(
    "",
    response_model=list[User],
)
async def get_all_users():
    return await User.all()


GET_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UserID):
    user = await User.get(user_id)
    if user is None:
        raise GET_USER_EXCEPTION
    return user


@router.get("/users_responses", response_model=list[TaskResponse])
async def get_all_users_responses():
    return await services.user.get_user_responses()


@router.get("/me/tasks", response_model=MyTasks)
async def get_my_tasks(user: User = Depends(current_active_user)):
    return await get_user_tasks(user.id)
