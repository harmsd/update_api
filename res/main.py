from typing import Annotated

from fastapi.staticfiles import StaticFiles
import uvicorn

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from sqlalchemy import select

from database import create_db_and_tables, SessionDep
from modules.users.models import User, UserPublic 
from modules.users.router import router as users_router
from auth.router import router as auth_router
from dashboard.router import router as dashboard_router
from home.router import router as home_router

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app = FastAPI()
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

app.include_router(home_router)
app.include_router(users_router, prefix="/users")
app.include_router(auth_router, prefix="/login")
app.include_router(dashboard_router, prefix="/dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/setup_database')
async def setup_database():
    await create_db_and_tables()
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)