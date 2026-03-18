from fastapi.responses import FileResponse
import uvicorn

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from sqlalchemy import select

from database import create_db_and_tables

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend/auth/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    login: str
    password: str

@app.post("/login")
async def login(data: LoginRequest):
    return {"message": "OK"}

@app.get("/login")
async def login():
    return FileResponse("frontend/auth/templates/index.html")

@app.post('/setup_database')
async def setup_database():
    await create_db_and_tables()
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)