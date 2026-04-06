from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from auth.services import get_current_user_from_cookie
from modules.users.models import User

router = APIRouter(prefix="/main", tags=["main"])
organizations_router = APIRouter(prefix="/organizations", tags=["organizations"])
settings_router = APIRouter(prefix="/settings", tags=["settings"])

templates = Jinja2Templates(directory="../frontend/templates")


@organizations_router.get("/")
async def organizations_page(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
):
    return templates.TemplateResponse(
        "/dashboard/organizations.html",
        {"request": request, "user": current_user}
    )


@settings_router.get("/")
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
):
    return templates.TemplateResponse(
        "/dashboard/settings.html",
        {"request": request, "user": current_user}
    )


@router.get("/", response_class=HTMLResponse)
async def licenses_page(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
):
    return templates.TemplateResponse(
        "/dashboard/licenses.html",
        {"request": request, "user": current_user}
    )