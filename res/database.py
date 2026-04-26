from typing import Annotated

from fastapi import Depends, APIRouter

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from modules.users.models import User
from modules.licenses.models import License

router = APIRouter(prefix="/db", tags=["db"])

engine = create_async_engine("sqlite+aiosqlite:///data.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

async def get_license(session: AsyncSession):
    result = await session.execute(
        ...
    )

@router.post('/setup')
async def setup_database():
    await create_db_and_tables()
    return {"ok": True}