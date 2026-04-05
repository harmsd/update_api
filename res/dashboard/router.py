from fastapi import APIRouter, Depends, File, HTTPException, Request, status
from fastapi import security
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
import json

from pydantic import BaseModel

from modules.users.models import User


router = APIRouter(prefix="/main", tags=["main"])
organizations_router = APIRouter(prefix="/organizations", tags=["organizations"])
settings_router = APIRouter(prefix="/settings", tags=["settings"])
security = HTTPBearer()

templates = Jinja2Templates(directory="../frontend/templates")

@organizations_router.get("/")
async def organizations_page(request: Request):
    return templates.TemplateResponse("/dashboard/organizations.html", {"request": request})

@settings_router.get("/")
async def settings_page(request: Request):
    return templates.TemplateResponse("/dashboard/settings.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def licenses_page(request: Request):
    return templates.TemplateResponse("/dashboard/licenses.html", {"request": request})


    

