from fastapi.staticfiles import StaticFiles
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import router as db_router
from modules.users.router import router as users_router
from modules.licenses.router import router as licenses_router
from home.router import router as home_router
from auth.router import auth_router
from auth.router import jwt_router
from dashboard.router import router as main_router
from dashboard.router import organizations_router
from dashboard.router import settings_router
from update.router import router as update_router

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app = FastAPI()
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

app.include_router(db_router)
app.include_router(users_router)
app.include_router(licenses_router)
app.include_router(home_router)
app.include_router(main_router)
app.include_router(organizations_router)
app.include_router(settings_router)
app.include_router(auth_router)
app.include_router(jwt_router)
app.include_router(update_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)