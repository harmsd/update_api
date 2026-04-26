from fastapi import Depends, File, HTTPException, Query, APIRouter, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import select
from typing import Annotated
from datetime import datetime, date
import json

from database import SessionDep
from modules.licenses.models import *
from modules.users.models import User
from exceptions import user_not_found
from dashboard.services import to_decrypt
from auth.services import require_admin

router = APIRouter(prefix="/licenses")

@router.post("/upload-enc")
async def upload_enc(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
):
    if not file.filename.lower().endswith(".enc"):
        raise HTTPException(status_code=400, detail="Allowed only .enc files")
    try:
        content = await to_decrypt(file)
    except json.JSONDecodeError:
        return JSONResponse({"error": "Incorrect file format"}, status_code=400)
    return content

@router.post("/", response_model=LicensePublic)
async def create_license(
    payload: LicenseFromFront,
    session: SessionDep,
    _: User = Depends(require_admin),
):

    try:
        end_date = datetime.strptime(payload.organization.expiry, "%d.%m.%Y").date() \
            if isinstance(payload.organization.expiry, str) \
            else payload.organization.expiry
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Ожидается ДД.ММ.ГГГГ")

    db_license = License(
        name=payload.organization.name,
        inn=payload.organization.inn,
        email=payload.organization.email,
        tariff=payload.organization.tariff,
        disabled=False,
        hostname=payload.host.hostname,
        os=payload.host.os,
        mac=payload.host.mac,
        uuid=payload.host.uuid,
        comment=payload.host.comment,
        start_date=date.today(),
        end_date=end_date,
        checksum=payload.checksum.value
    )

    session.add(db_license)
    await session.commit()
    await session.refresh(db_license)

    return db_license

@router.get("/", response_model=list[LicensePublic])
async def read_licenses(
    session: SessionDep,
    _: User = Depends(require_admin),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    result = await session.execute(
        select(License).offset(offset).limit(limit)
    )
    return result.scalars().all()

@router.get("/{license_id}", response_model=LicensePublic)
async def read_license(
    license_id: int,
    session: SessionDep,
    _: User = Depends(require_admin),
):
    db_license = await session.get(License, license_id)
    if not db_license:
        raise user_not_found
    return db_license

@router.patch("/{license_id}", response_model=LicensePublic)
async def update_license(
    license_id: int,
    payload: LicenseFromFront,
    session: SessionDep,
    _: User = Depends(require_admin),
):
    db_license = await session.get(License, license_id)
    if not db_license:
        raise user_not_found

    try:
        end_date = (
            datetime.strptime(payload.organization.expiry, "%d.%m.%Y").date()
            if isinstance(payload.organization.expiry, str)
            else payload.organization.expiry
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Ожидается ДД.ММ.ГГГГ"
        )

    db_license.name     = payload.organization.name
    db_license.inn      = payload.organization.inn
    db_license.email    = payload.organization.email
    db_license.tariff   = payload.organization.tariff
    db_license.hostname = payload.host.hostname
    db_license.os       = payload.host.os
    db_license.mac      = payload.host.mac
    db_license.uuid     = payload.host.uuid
    db_license.comment  = payload.host.comment
    db_license.end_date = end_date
    db_license.checksum = payload.checksum.value

    session.add(db_license)
    await session.commit()
    await session.refresh(db_license)

    return db_license

@router.delete("/{license_id}")
async def delete_license(
    license_id: int,
    session: SessionDep,
    _: User = Depends(require_admin),
):
    db_license = await session.get(License, license_id)
    if not db_license:
        raise user_not_found
    await session.delete(db_license)
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