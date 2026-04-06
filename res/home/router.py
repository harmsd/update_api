from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from auth import utils as auth_utils
from jwt.exceptions import InvalidTokenError

router = APIRouter(tags=["home"])

@router.get("/")
async def home(request: Request):
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

    return RedirectResponse(url="/login/", status_code=302)