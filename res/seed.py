"""
Run once to create the initial admin user:
    ADMIN_PASSWORD=yourpassword python seed.py
"""
import asyncio
import os
import sys

from database import new_session, create_db_and_tables, get_user_by_username
from modules.users.models import User
from auth.utils import hash_password


async def seed():
    password = os.environ.get("ADMIN_PASSWORD")
    if not password:
        print("Error: set ADMIN_PASSWORD env var before running seed.py")
        sys.exit(1)

    await create_db_and_tables()

    async with new_session() as session:
        existing = await get_user_by_username(session, "admin")
        if existing:
            print("Admin user already exists, skipping.")
            return

        admin = User(
            name="Administrator",
            username="admin",
            password=hash_password(password),
            organization="KAPRIS",
            role="admin",
            email="admin@example.com",
            disabled=False,
        )
        session.add(admin)
        await session.commit()
        print("Admin user created successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
