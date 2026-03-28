from fastapi import Depends, FastAPI, HTTPException, Query, APIRouter
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated

from database import SessionDep

from modules.users.models import *

router = APIRouter()

@router.post("/", response_model=UserPublic)
async def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    hashed_password = user.hashed_password
    db_user.hashed_password = hashed_password
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.get("/", response_model=list[UserPublic])
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    result = await session.execute(select(User).offset(offset).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, session: SessionDep):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(user_id: int, user: UserUpdate, session: SessionDep):
    user_db = await session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)
    return user_db 

@router.delete("/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    await session.commit()
    return {"ok": True}


'''
@app.post("/users")
async def add_user(data: UserCreate, session: SessionDep):
    new_user = UserCreate(
        name=data.name,
        login=data.login,
        pwd_hash=data.pwd_hash,
        role=data.role,
        organization=data.organization,
        email=data.email,
        account_status=data.account_status
    )
    db_user = User.model_validate(new_user)
    session.add(db_user)
    await session.commit()
'''