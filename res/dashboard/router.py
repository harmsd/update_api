from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from auth.utils import get_current_user_from_cookie
from modules.users.models import User

router = APIRouter()

@router.get("/")
async def dashboard(): #current_user: User = Depends(get_current_user_from_cookie)
    return FileResponse("../frontend/templates/dashboard/main.html")