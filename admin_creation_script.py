from services.user import create_admin
import asyncio
user = asyncio.run(create_admin())
print(user.id)