from fastapi import APIRouter, Depends, status

import services.user
from apis.utils import AUTH_RESPONSES, NOT_FOUND_HTTP_EXCEPTION, check_auth
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


@user_router.patch(
    "/users",
    status_code=202,
    response_description="Successfully updated user",
    responses={
        NOT_FOUND_HTTP_EXCEPTION.status_code: {"model": ErrorResponse, "description": NOT_FOUND_HTTP_EXCEPTION.detail}
    } | AUTH_RESPONSES,
    dependencies=[Depends(check_auth(True))]
)
async def update_user(user: PartialUser):
    updated = await services.user.update_user(user)
    if not updated:
        raise NOT_FOUND_HTTP_EXCEPTION
    
@user_router.delete(
    "/users/{user_id_to_be_deleted}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Successfully deleted user",
    responses={
        NOT_FOUND_HTTP_EXCEPTION.status_code: {"model": ErrorResponse, "description": NOT_FOUND_HTTP_EXCEPTION.detail}
    } | AUTH_RESPONSES,
    dependencies=[Depends(check_auth(True))]
)
async def delete_user(user_id_to_be_deleted: str):
    deleted = await services.user.delete_user(user_id_to_be_deleted)
    if not deleted:
        raise NOT_FOUND_HTTP_EXCEPTION