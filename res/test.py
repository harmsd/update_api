import asyncio
from database import new_session, get_user

async def print_user():
    async with new_session() as session:
        user = await get_user(session, "harms")
        print(user)

asyncio.run(print_user())