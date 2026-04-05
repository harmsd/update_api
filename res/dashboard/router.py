from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi import security
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from modules.users.models import User

router = APIRouter(prefix="/licenses", tags=["licenses"])
organizations_router = APIRouter(prefix="/organizations", tags=["organizations"])
settings_router = APIRouter(prefix="/settings", tags=["settings"])
security = HTTPBearer()

class Distribution(BaseModel):
    name: str
    start: str
    end: str

@organizations_router.get("/")
async def organizations():
    return FileResponse("../frontend/templates/dashboard/organizations.html")

@settings_router.get("/")
async def settings():
    return FileResponse("../frontend/templates/dashboard/settings.html")

@router.get("/")
async def dashboard(): 
    return FileResponse("../frontend/templates/dashboard/licenses.html")
