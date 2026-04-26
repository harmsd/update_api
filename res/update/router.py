from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from modules.users.models import User

from auth.services import get_current_user_from_cookie

updates_router = APIRouter(prefix="/updates", tags=["updates"])
license_router = APIRouter(prefix="/license", tags=["license"])
support_router = APIRouter(prefix="/support", tags=["support"])

@updates_router.get("/")
async def update(
    user: User = Depends(get_current_user_from_cookie),
):
    return FileResponse("../onyx-frontend/templates/update/updates.html")

@license_router.get("/")
async def license(
    user: User = Depends(get_current_user_from_cookie),
):
    return FileResponse("../onyx-frontend/templates/update/license.html")

@support_router.get("/")
async def support(
    user: User = Depends(get_current_user_from_cookie),
):
    return FileResponse("../onyx-frontend/templates/update/support.html")