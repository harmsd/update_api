from fastapi import APIRouter, Depends
from fastapi.responses import Response
from fastapi.responses import FileResponse

from modules.users.models import User
from auth import utils as auth_utils
from auth.services import validate_auth_user, get_current_active_auth_user
from auth.models import TokenData

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
        "role": user.role
    }

    token = auth_utils.encode_jwt(jwt_payload)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=3600
    )

    return TokenData (
        access_token=token,
        token_type="Bearer"
    )

@jwt_router.get('/users/me/')
def auth_user_check_self_info(
     user: User = Depends(get_current_active_auth_user),
):
     return {
        "username": user.username,
        "role": user.role,
     }

@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "remove token"}



