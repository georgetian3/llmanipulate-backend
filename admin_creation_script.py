from services.user import create_admin
import asyncio
from services.user import User
user = asyncio.run(create_admin())
print(user.id)