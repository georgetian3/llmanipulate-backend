# from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import UUID4

from models.task import TaskResponse

# import services.responses
# from models.response import Response, ResponseCreate
# from models.user import User
# from services.user import current_active_user, current_superuser

router = APIRouter(prefix="/responses")


@router.post("")
async def create_response(task_id: UUID4, response: TaskResponse): ...


# @router.post(
#     "/submit_response",
#     response_model=Response,
# )
# async def create_response(
#     new_response: ResponseCreate, user: User = Depends(current_active_user)
# ):
#     response = await services.responses.create_response(
#         new_response
#     )  # Call the service function
#     if not response:
#         raise HTTPException(status_code=500, detail="Error saving response to database")
#     return response


# @router.get("/responses_by_user")
# async def get_responses_by_user(user_id: Annotated[str, Header]):
#     return await services.responses.get_responses_by_users(user_id)


# @router.get("/responses", dependencies=[Depends(current_superuser)])
# async def get_responses():
#     return await services.responses.get_responses()
