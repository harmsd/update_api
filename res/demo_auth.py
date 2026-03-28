from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jwt.exceptions import InvalidTokenError

from modules.users.models import User
from auth import utils as auth_utils
from auth.models import TokenData

router = APIRouter(prefix="/jwt", tags=["JWT"])
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
        unauthed_exc = HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="invalid username or password",
        )

        if not (user := users_db.get(username)):
            raise unauthed_exc
        
        if not auth_utils.validate_password(
              password=password,
              hashed_password=user.password,
        ):
            raise unauthed_exc
        
        if user.disabled:
             raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail="user is disabled"
             )
        
        return user

def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = auth_utils.decode_jwt(
            token=token
        )
    except InvalidTokenError as e:
         raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail=f"Invalid token error:" 
         )
    return payload

def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
) -> User:
        username: str | None = payload.get("username")
        if user := users_db.get(username):
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token not found",
        )

def get_current_active_auth_user(
    user: User = Depends(get_current_auth_user),
):
     if not user.disabled:
        return user
     raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user is disabled"
     )

@router.post("/login/", response_model=TokenData)
def auth_user_issue_jwt(
    user: User = Depends(validate_auth_user),
):
    
    jwt_payload = {
        "sub": f"{user.id}",
        "username": user.username,
        "email": user.email
    }

    token = auth_utils.encode_jwt(jwt_payload)
    return TokenData (
        access_token=token,
        token_type="Bearer"
    )


@router.get('/users/me/')
def auth_user_check_self_info(
     user: User = Depends(get_current_active_auth_user),
):
     return {
        "username": user.username,
        "email": user.email,
     }