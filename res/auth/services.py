from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer

from jwt.exceptions import InvalidTokenError

from modules.users.models import User
from auth import utils as auth_utils
from auth.models import TokenData
from exceptions import invalid_username_or_password, user_is_disabled, invalid_token_error, token_not_found

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")

harms = User(
    id=1,
    name="Danek",
    username="harms",
    password=auth_utils.hash_password("harms"),
    disabled=False,
    organization="KAPRIS",
    role="admin",
    email="harms@example.com"
)

users_db: dict[str, User] = {
    harms.username: harms
}

def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
):
    if not (user := users_db.get(username)):
        raise invalid_username_or_password
    
    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise invalid_username_or_password
    
    if user.disabled: 
        raise user_is_disabled
    return user

def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = auth_utils.decode_jwt(
            token=token
        )
    except InvalidTokenError:
        raise invalid_token_error
    return payload

def get_current_auth_user( 
        payload: dict = Depends(get_current_token_payload),
) -> User:
    username: str | None = payload.get("username")
    if user := users_db.get(username):
        return user
    raise token_not_found

def get_current_active_auth_user(
    user: User = Depends(get_current_auth_user)
):
    if user.disabled:
        raise user_is_disabled
    return user






