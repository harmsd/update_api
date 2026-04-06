from fastapi import (
    Depends, 
    HTTPException,
    Request, 
    status, 
    Form
)
from fastapi.security import OAuth2PasswordBearer

from jwt.exceptions import InvalidTokenError

from auth.helpers import (
    create_access_token,
    TOKEN_TYPE_FIELD,
    REFRESH_TOKEN_TYPE,
    ACCESS_TOKEN_TYPE,
)
from modules.users.models import User
from auth import utils as auth_utils
from auth.models import TokenData
from exceptions import (
    invalid_username_or_password, 
    user_is_disabled, 
    invalid_token_error, 
    token_not_found,
)


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

# refresh token
def get_current_auth_user_for_refresh():
    pass

def auth_refresh_jwt(
    user: User = Depends(get_current_auth_user_for_refresh)
):
    access_token = create_access_token(user)
    return TokenData(
        access_token=access_token,
    )

def validate_token_type(
        payload: dict,
        token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invald token type {current_token_type!r} expected {token_type!r}" 
    )

def get_user_by_token_sub(payload: dict) -> User:
    username: str | None = payload.get("sub")
    if user := users_db.get(username):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )

def get_auth_user_from_token_of_type(token_type: str):
    def get_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
    ) -> User:
        validate_token_type(payload, token_type)
        return get_user_by_token_sub(payload)
    
    return get_auth_user_from_token

class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
    ):
        validate_token_type(payload, self.token_type)
        return get_user_by_token_sub(payload)
    
get_current_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)


def get_current_user_from_cookie(request: Request) -> User:
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

    if user := users_db.get(username):
        if user.disabled:
            raise user_is_disabled
        return user

    raise HTTPException(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        headers={"Location": "/login/"},
    )