from collections import defaultdict
import time

from fastapi import Depends, HTTPException, Request, status, Form
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from auth.helpers import TOKEN_TYPE_FIELD, REFRESH_TOKEN_TYPE, ACCESS_TOKEN_TYPE
from modules.users.models import User
from auth import utils as auth_utils
from database import SessionDep, get_user_by_username, get_user_by_id
from exceptions import (
    invalid_username_or_password,
    user_is_disabled,
    invalid_token_error,
)

_failed_attempts: dict[str, list[float]] = defaultdict(list)
_block_until: dict[str, float] = {}

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60
BLOCK_SECONDS = 300

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError:
        raise invalid_token_error
    return payload


def validate_token_type(payload: dict, token_type: str) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type!r} expected {token_type!r}",
    )


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        session: SessionDep,
        payload: dict = Depends(get_current_token_payload),
    ) -> User:
        validate_token_type(payload, self.token_type)
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")
        user = await get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token invalid (user not found)",
            )
        return user


get_current_auth_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)


def get_current_active_auth_user(
    user: User = Depends(get_current_auth_user),
) -> User:
    if user.disabled:
        raise user_is_disabled
    return user


async def validate_auth_user(
    request: Request,
    session: SessionDep,
    username: str = Form(),
    password: str = Form(),
) -> User:
    ip = request.client.host
    now = time.time()

    block_end = _block_until.get(ip, 0)
    if now < block_end:
        seconds_left = int(block_end - now)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Слишком много попыток. Попробуйте через {seconds_left} сек.",
        )

    _failed_attempts[ip] = [t for t in _failed_attempts[ip] if now - t < WINDOW_SECONDS]

    user = await get_user_by_username(session, username)
    if not user:
        _failed_attempts[ip].append(now)
        if len(_failed_attempts[ip]) >= MAX_ATTEMPTS:
            _block_until[ip] = now + BLOCK_SECONDS
            _failed_attempts.pop(ip, None)
        raise invalid_username_or_password

    if not auth_utils.validate_password(password=password, hashed_password=user.password):
        _failed_attempts[ip].append(now)
        if len(_failed_attempts[ip]) >= MAX_ATTEMPTS:
            _block_until[ip] = now + BLOCK_SECONDS
            _failed_attempts.pop(ip, None)
        raise invalid_username_or_password

    if user.disabled:
        raise user_is_disabled

    _failed_attempts.pop(ip, None)
    _block_until.pop(ip, None)
    return user


async def get_current_user_from_cookie(request: Request, session: SessionDep) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login/"},
            detail="Not authenticated",
        )

    try:
        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login/"},
            detail="Invalid token",
        )

    username: str | None = payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login/"},
        )

    user = await get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login/"},
        )
    if user.disabled:
        raise user_is_disabled
    return user


def require_role(*roles: str):
    async def dependency(user: User = Depends(get_current_user_from_cookie)) -> User:
        if user.role not in roles:
            redirect_url = "/updates/" if user.role == "user" else "/main/"
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": redirect_url},
            )
        return user
    return dependency


require_admin = require_role("admin")
require_user  = require_role("user")
