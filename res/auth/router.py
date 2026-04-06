from typing import Any
import uuid
from time import time

from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Request
from fastapi.responses import Response, FileResponse, RedirectResponse
from jwt import InvalidTokenError
from starlette import status

from modules.users.models import User, UserPublic, UserUpdate
from auth import utils as auth_utils
from auth.services import validate_auth_user, get_current_active_auth_user
from auth.models import TokenData
from database import SessionDep
from auth.services import users_db

jwt_router = APIRouter(prefix="/jwt", tags=["JWT"])
auth_router = APIRouter(prefix="/login", tags=["auth"])

@auth_router.get("/")
async def login():
    return FileResponse("../frontend/templates/auth/login.html")

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
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 15,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/jwt/refresh",
    )

    return TokenData(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
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

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    return TokenData(
        access_token=new_access_token,
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

# @jwt_router.patch("/users/me", response_model=UserPublic)
# def update_me(
#     data: UserUpdate,
#     request: Request,
#     session: SessionDep,
# ):
#     user_id = request.session.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Не авторизован")

#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")

#     update_data = data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(user, field, value)

#     session.add(user)
#     session.commit()
#     session.refresh(user)
#     return user

@auth_router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login/", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/jwt/refresh")
    return response

usernames_to_passwords = {
    "admin": "admin",
    "john": "password",
}


static_auth_token_to_username = {
    "a0787852e766b02e87f6dd15e4c3d1f1": "admin",
    "a14f178e75dee69fa66ff3fad9db0daa": "john",
}

def get_username_by_static_auth_token(
    static_token: str = Header(alias="x-auth-token"),
) -> str:
    if username := static_auth_token_to_username.get(static_token):
        return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid",
    )

@auth_router.get("/some-http-header-auth/")
def demo_auth_some_http_header(
    username: str = Depends(get_username_by_static_auth_token),
):
    return {
        "message": f"Hi, {username}!",
        "username": username,
    }


COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex

def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
) -> dict:
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )

    return COOKIES[session_id]

@auth_router.post("/login-cookie/")
def demo_auth_login_set_cookie(
    response: Response,
    username: str = Depends(get_username_by_static_auth_token),
):
    session_id = generate_session_id()
    COOKIES[session_id] = {
        "username": username,
        "login_at": int(time()),
    }
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok"}

@auth_router.get("/check-cookie/")
def demo_auth_check_cookie(
    user_session_data: dict = Depends(get_session_data),
):
    username = user_session_data["username"]
    return {
        "message": f"Hello, {username}!",
        **user_session_data,
    }

@auth_router.get("/logout-cookie/")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
):
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIE_SESSION_ID_KEY)
    username = user_session_data["username"]
    return {
        "message": f"Bye, {username}!",
    }