import sys
from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import ValidationError

from apis.utils import AUTH_RESPONSES, check_auth
import services.responses
from models.models import NewResponse, Response

response_router = APIRouter()

@response_router.post( "/submit_response", response_model=Response)
async def create_response(new_response: NewResponse):
    response = await services.responses.create_response(new_response)  # Call the service function
    if not response:
        raise HTTPException(status_code=500, detail="Error saving response to database")
    return response

@response_router.get("/responses_by_user")
async def get_responses_by_user(user_id: Annotated[str, Header]):
    return await services.responses.get_responses_by_users(user_id)

@response_router.get( "/responses", responses=AUTH_RESPONSES, dependencies=[Depends(check_auth(True))] )
async def get_responses():
    return await services.responses.get_responses()