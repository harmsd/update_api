from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi import security
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
import json

from pydantic import BaseModel

from modules.users.models import User
from dashboard.services import to_decrypt

router = APIRouter(prefix="/licenses", tags=["licenses"])
organizations_router = APIRouter(prefix="/organizations", tags=["organizations"])
settings_router = APIRouter(prefix="/settings", tags=["settings"])
security = HTTPBearer()

templates = Jinja2Templates(directory="../frontend/templates")

class Distribution(BaseModel):
    name: str
    start: str
    end: str

@organizations_router.get("/")
async def organizations():
    return FileResponse("../frontend/templates/dashboard/organizations.html")

@settings_router.get("/")
async def settings_page(request: Request):
    return templates.TemplateResponse("/dashboard/settings.html", {"request": request})

# @router.get("/")
# async def licenses(): 
#     return FileResponse("../frontend/templates/dashboard/licenses.html")

@router.get("/", response_class=HTMLResponse)
async def licenses_page(request: Request):
    return templates.TemplateResponse("/dashboard/licenses.html", {"request": request})

@router.post("/upload-enc")
async def upload_enc(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".enc"):
        raise HTTPException(status_code=400, detail="Allowed only .enc files")
    
    try:
        content = await to_decrypt(file)
    except json.JSONDecodeError:
        return JSONResponse({"error": "Incorrect file format"}, status_code=400)
    
    return content
    
    
