from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/updates", tags=["updates"])

@router.get("/")
async def update():
    return FileResponse("../frontend/templates/update/main.html")