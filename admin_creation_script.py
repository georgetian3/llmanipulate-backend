import asyncio

from services.user import create_admin

user = asyncio.run(create_admin())
print(user.id)
