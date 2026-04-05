from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["home"])

@router.get("/")
async def home():
    return FileResponse("../frontend/templates/index.html")