from fastapi import APIRouter, Form, Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

from pydantic import BaseModel

from typing import Annotated
from datetime import timedelta

from database import SessionDep
from auth.models import Token
from auth.utils import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
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


@router.post("/")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user["username"]}, expires_delta=access_token_expires)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        samesite="None", # для теста куков, потом поставить "lax"
        secure=False # для теста куков
    )
    return {"message": "Авторизация успешна"}

@router.get("/")
async def login():
    return FileResponse("../frontend/templates/auth/login.html")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "remove token"}



