from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, FileResponse, RedirectResponse
from jwt import InvalidTokenError

from modules.users.models import User
from auth import utils as auth_utils
from auth.services import validate_auth_user, get_current_active_auth_user
from auth.models import TokenData
from auth.services import users_db

jwt_router = APIRouter(prefix="/jwt", tags=["JWT"])
auth_router = APIRouter(prefix="/login", tags=["auth"])

_SECURE_COOKIES = True  # set False only in local dev without HTTPS

@auth_router.get("/")
async def login(request: Request):
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = auth_utils.decode_jwt(token)
            role = payload.get("role")
            return RedirectResponse(
                url="/main/" if role == "admin" else "/updates/",
                status_code=302
            )
        except InvalidTokenError:
            pass
    return FileResponse("../onyx-frontend/templates/auth/login.html")

@jwt_router.post("/login", response_model=TokenData)
def auth_user_issue_jwt(
    response: Response,
    user: User = Depends(validate_auth_user),
):
    jwt_payload = {
        "sub": f"{user.id}",
        "username": user.username,
        "role": user.role,
    }

    access_token = auth_utils.encode_jwt(jwt_payload)
    refresh_token = auth_utils.encode_refresh_jwt(jwt_payload)

    response.set_cookie(
        key="access_token", value=access_token,
        httponly=True, samesite="lax", secure=_SECURE_COOKIES,
        max_age=60 * 15, path="/",
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, samesite="lax", secure=_SECURE_COOKIES,
        max_age=60 * 60 * 24 * 7, path="/",
    )

    return TokenData(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        role=user.role,
    )

@jwt_router.post("/refresh", response_model=TokenData)
def refresh_access_token(
    request: Request,
    response: Response,
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token не найден")

    try:
        payload = auth_utils.decode_jwt(refresh_token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Refresh token недействителен или истёк")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Неверный тип токена")

    sub = payload.get("sub")
    user = next((u for u in users_db.values() if str(u.id) == sub), None)
    if not user or user.disabled:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    new_payload = {"sub": str(user.id), "username": user.username, "role": user.role}
    new_access_token = auth_utils.encode_jwt(new_payload)
    new_refresh_token = auth_utils.encode_refresh_jwt(new_payload)

    response.set_cookie(
        key="access_token", value=new_access_token,
        httponly=True, samesite="lax", secure=_SECURE_COOKIES,
        max_age=60 * 15, path="/",
    )
    response.set_cookie(
        key="refresh_token", value=new_refresh_token,
        httponly=True, samesite="lax", secure=_SECURE_COOKIES,
        max_age=60 * 60 * 24 * 7, path="/",
    )

    return TokenData(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="Bearer",
    )


@jwt_router.get('/users/me/')
def auth_user_check_self_info(
     user: User = Depends(get_current_active_auth_user),
):
     return {
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "role": user.role,
     }

@auth_router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login/", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response
