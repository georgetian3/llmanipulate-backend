from apis.base import api
from models.models import NewUser
import services.user

@api.post('/user')
async def create_user(new_user: NewUser):
    user = await services.user.create_user(new_user)
    