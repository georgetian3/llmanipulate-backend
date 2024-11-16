import services.user
from apis.base import api
from models.models import NewUser, User


@api.post("/user", response_model=User)
async def create_user(new_user: NewUser):
    user = await services.user.create_user(new_user)
    return user
