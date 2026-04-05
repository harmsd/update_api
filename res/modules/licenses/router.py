from fastapi import HTTPException, Query, APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Annotated

from database import SessionDep
from modules.licenses.models import *
from exceptions import user_not_found

router = APIRouter(prefix="/license", tags=["licenses"])

@router.post("/", response_model=LicensePublic)
async def create_license(license_in: LicenseCreate, session: SessionDep):
    
    db_license = License(
        organization=license_in.organization,
        disabled=license_in.disabled,
        start_date=license_in.start_date,
        end_date=license_in.end_date
    )
    
    session.add(db_license)
    await session.commit()
    await session.refresh(db_license)
    
    return db_license

@router.get("/", response_model=list[LicensePublic])
async def read_licenses(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    result = await session.execute(select(license).offset(offset).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/{license_id}", response_model=LicensePublic)
async def read_license(user_id: int, session: SessionDep):
    user = await session.get(License, user_id)
    if not user:
        raise user_not_found
    return user

@router.patch("/{license_id}", response_model=LicensePublic)
async def update_license(license_id: int, user: LicenseUpdate, session: SessionDep):
    user_db = await session.get(License, license_id)
    if not user_db:
        raise user_not_found
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)
    return user_db 

@router.delete("/{license_id}")
async def delete_license(license_id: int, session: SessionDep):
    user = await session.get(License, license_id)
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