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

@response_router.get(
    "/responses",
    response_model=list[Response],
    responses=AUTH_RESPONSES,
    dependencies=[Depends(check_auth(True))]
)
async def get_responses():
    await services.responses.get_responses()