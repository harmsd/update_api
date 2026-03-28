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
from modules.users.models import User
router = APIRouter(prefix="/login", tags=["login"])


@router.get("/")
async def login():
    return FileResponse("../frontend/templates/auth/login.html")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "remove token"}



