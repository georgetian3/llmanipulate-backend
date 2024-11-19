from fastapi import APIRouter

from models.models import Response
import services.responses


response_router = APIRouter()

@response_router.post('/responses')
async def create_response(response: Response):
    await services.responses.create_response(response)