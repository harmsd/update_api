from fastapi import HTTPException, Query, APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Annotated

from database import SessionDep

from auth.utils import hash_password
from auth.services import get_current_user_from_cookie
from modules.users.models import User, UserUpdate, UserPublic, UserCreate
from exceptions import user_not_found

router = APIRouter(prefix="/user", tags=["users"])

@router.post("/", response_model=UserPublic)
async def create_user(user_in: UserCreate, session: SessionDep):

    hashed_password = hash_password(user_in.password_string)
    
    db_user = User(
        name=user_in.name,
        username=user_in.username,
        password=hashed_password,
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
        raise user_not_found
    return user

@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: int, 
    user: UserUpdate, 
    session: SessionDep,
    current_user: User = Depends(get_current_user_from_cookie)
    ):
    user_db = await session.get(User, user_id)
    if not user_db:
        raise user_not_found
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
        raise user_not_found
    await session.delete(user)
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