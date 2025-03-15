from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4, BaseModel

import services.responses
import services.user
from apis.auth import EXCEPTION_403, current_admin, current_user
from models.task import TaskReadParticipant, TaskResponse
from models.user import User, UserCreate, UserID, UserRead
from services.tasks import get_participant_tasks
from settings import SETTINGS

router = APIRouter(prefix="/users")


CREATE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User email already taken"
)


@router.put(
    "",
    description="Creates a new participant. Requires an admin's user_id for authentication.",
    response_model=User,
    dependencies=[Depends(current_admin)],
)
async def create_user(new_user: UserCreate):
    return await services.user.create_participant(new_user)


@router.get("", response_model=list[UserRead], dependencies=[Depends(current_admin)])
async def get_users():
    return [UserRead.model_validate(user) for user in await User.all()]


GET_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)


@router.get("/me", response_model=UserRead)
async def get_me(user_id: UUID | None = Depends(current_user)):
    user = await User.get(user_id)
    if user:
        return UserRead.model_validate(user)
    raise EXCEPTION_403


class LoginRequired(BaseModel):
    login_required: bool


@router.get("/login-required", response_model=LoginRequired)
async def login_required():
    return LoginRequired(login_required=SETTINGS.login_required)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UserID):
    user = await User.get(user_id)
    if user is None:
        raise GET_USER_EXCEPTION
    return user


@router.get("/{user_id}/responses", response_model=list[TaskResponse])
async def get_user_responses(user_id: UUID4):
    return await services.responses.get_user_responses(user_id)


@router.get("/me/tasks", response_model=list[TaskReadParticipant])
async def get_my_tasks(user_id: UUID | None = Depends(current_user)):
    if SETTINGS.login_required and not user_id:
        raise EXCEPTION_403
    return await get_participant_tasks(user_id)
