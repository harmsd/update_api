from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from auth.services import require_admin, require_user
from modules.users.models import User

router = APIRouter(prefix="/main", tags=["main"])
organizations_router = APIRouter(prefix="/organizations", tags=["organizations"])
settings_router = APIRouter(prefix="/settings", tags=["settings"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])

templates = Jinja2Templates(directory="../onyx-frontend/templates")


@organizations_router.get("/")
async def organizations_page(
    request: Request,
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="/dashboard/organizations.html",
        context={
            "user": current_user,
            "sidebar": "/partials/_sidebar_admin.html"
        }
    )


@settings_router.get("/")
async def settings_page(
    request: Request,
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="/dashboard/settings.html",
        context={
            "user": current_user,
            "sidebar": "/partials/_sidebar_admin.html"
        }
    )


@router.get("/", response_class=HTMLResponse)
async def licenses_page(
    request: Request,
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="/dashboard/licenses.html",
        context={
            "user": current_user,
            "sidebar": "/partials/_sidebar_admin.html"
        }
    )


@admin_router.get("/", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="/dashboard/admin.html",
        context={
            "user": current_user,
            "sidebar": "/partials/_sidebar_admin.html",
        }
    )