import uvicorn

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from sqlalchemy import select


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["http://127.0.0.1:8000"],
    allow_headers=["http://127.0.0.1:8000"],
)

app.mount("/frontend/auth/css", StaticFiles(directory="css"), name="styles.css")
templates = Jinja2Templates(directory="")

@app.get("/")
async def home():
    return FileResponse("../frontend/auth/index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)