from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi import security
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from demo_auth import get_current_active_auth_user
from modules.users.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
security = HTTPBearer()

class Distribution(BaseModel):
    name: str
    start: str
    end: str

@router.get("/")
async def dashboard(): 
    return FileResponse("../frontend/templates/dashboard/main.html")

@router.get("/distributions", response_model=list[Distribution])
async def get_distributions(
    user: User = Depends(get_current_active_auth_user)
) -> list[Distribution]:
    distributions = [
        Distribution(name="Distro 1", start="2024-01-01", end="2024-12-31"),
        Distribution(name="Distro 2", start="2025-01-01", end="2025-12-31"),
    ]
    return distributions

@router.get("/check-auth")  
async def check_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: User = Depends(get_current_active_auth_user)
):
    return {"status": "ok", "user_id": user.id} 