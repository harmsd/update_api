from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

from pydantic import BaseModel

from typing import Annotated
from datetime import timedelta

from database import SessionDep
from auth.models import Token
from auth.utils import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class LoginRequest(BaseModel):
    login: str
    password: str


@router.post("/")
async def login(data: LoginRequest):
    return {"message": "OK"}


@router.get("/")
async def login():
    return FileResponse("frontend/auth/templates/index.html")


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(SessionDep, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


