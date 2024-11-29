from typing import Annotated
from fastapi import APIRouter, Depends, Header

from apis.utils import AUTH_RESPONSES, check_auth
import services.responses
from models.models import NewResponse, Response

response_router = APIRouter()


@response_router.put(
    "/responses",
    response_model=Response,
    responses=AUTH_RESPONSES,
    dependencies=[Depends(check_auth(False))]
)
async def create_response(user_id: Annotated[str, Header], response: NewResponse):
    return await services.responses.create_response(user_id, response)

@response_router.get("/responses_by_user", responses=AUTH_RESPONSES, dependencies=[Depends(check_auth(True))] )
async def get_responses_by_user(user_id: Annotated[str, Header]):
    return await services.responses.get_responses_by_users(user_id)
@response_router.get( "/responses", responses=AUTH_RESPONSES, dependencies=[Depends(check_auth(True))] )
async def get_responses():
    return await services.responses.get_responses()