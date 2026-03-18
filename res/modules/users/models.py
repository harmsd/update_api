from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select

class UserBase(SQLModel):
    name: str = Field(index=None)
    organization: str
    email: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login: str
    pwd_hash: str
    role: str
    account_status: str

class UserPublic(UserBase):
    id: int

class UserCreate(UserBase):
    login: str
    pwd_hash: str

class UserUpdate(UserBase):
    name: str | None = None
    organization: str | None = None
    email: str | None = None
    role: str | None = None
    account_status: str | None = None
    pwd_hash: str | None = None