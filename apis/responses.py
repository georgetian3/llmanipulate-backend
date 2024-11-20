from fastapi import APIRouter

import services.responses
from models.models import Response

response_router = APIRouter()


@response_router.post("/responses")
async def create_response(response: Response):
    await services.responses.create_response(response)
