from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from modules.users.models import User

from auth.services import require_user

updates_router = APIRouter(prefix="/updates", tags=["updates"])
license_router = APIRouter(prefix="/license", tags=["license"])
support_router = APIRouter(prefix="/support", tags=["support"])

@updates_router.get("/")
async def updates_page(
    user: User = Depends(require_user),
):
    return FileResponse("../onyx-frontend/templates/update/updates.html")

@license_router.get("/")
async def license_page(
    user: User = Depends(require_user),
):
    return FileResponse("../onyx-frontend/templates/update/license.html")

@support_router.get("/")
async def support_page(
    user: User = Depends(require_user),
):
    return FileResponse("../onyx-frontend/templates/update/support.html")
