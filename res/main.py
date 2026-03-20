from typing import Annotated

import uvicorn

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import select

from database import create_db_and_tables, SessionDep
from modules.users.models import User, UserPublic 
from modules.users.router import router as users_router
from auth.router import router as auth_router

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app = FastAPI()
app.include_router(users_router, prefix="/users")
app.include_router(auth_router, prefix="/login")

app.mount("/static", StaticFiles(directory="frontend/auth/static"), name="static")

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