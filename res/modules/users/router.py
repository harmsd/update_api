from fastapi import Query, APIRouter, Depends
from sqlmodel import select
from typing import Annotated

from database import SessionDep
from auth.utils import hash_password
from auth.services import require_admin
from modules.users.models import User, UserUpdate, UserPublic, UserCreate
from exceptions import user_not_found

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserPublic)
async def create_user(
    user_in: UserCreate,
    session: SessionDep,
    _: User = Depends(require_admin),
):
    db_user = User(
        name=user_in.name,
        username=user_in.username,
        password=hash_password(user_in.password_string),
        organization=user_in.organization,
        role=user_in.role,
        email=user_in.email,
        disabled=False,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.get("/", response_model=list[UserPublic])
async def read_users(
    session: SessionDep,
    _: User = Depends(require_admin),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    result = await session.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserPublic)
async def read_user(
    user_id: int,
    session: SessionDep,
    _: User = Depends(require_admin),
):
    user = await session.get(User, user_id)
    if not user:
        raise user_not_found
    return user

@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: SessionDep,
    _: User = Depends(require_admin),
):
    user_db = await session.get(User, user_id)
    if not user_db:
        raise user_not_found
    user_db.sqlmodel_update(user_update.model_dump(exclude_unset=True))
    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)
    return user_db

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: SessionDep,
    _: User = Depends(require_admin),
):
    user = await session.get(User, user_id)
    if not user:
        raise user_not_found
    await session.delete(user)
    await session.commit()
    return {"ok": True}
