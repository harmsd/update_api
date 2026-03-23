from typing import Annotated

from fastapi import Depends

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from modules.users.models import User
from modules.licenses.models import License

engine = create_async_engine("sqlite+aiosqlite:///data.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_user(session: AsyncSession, username: str):
    result = await session.execute(
        select(User).where(User.username == username)
    )
    user = result.scalars().first()
    return user

async def get_licenses(session: AsyncSession):
    result = await session.execute(
        ...
    )

