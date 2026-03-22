from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select

class UserBase(SQLModel):
    name: str = Field(index=None)
    organization: str
    role: str
    email: str
    disabled: bool

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    username: str = Field(unique=True, index=True)
    hashed_password: str
    role: str
    disabled: bool

class UserPublic(UserBase):
    id: int

class UserCreate(UserBase):
    username: str
    hashed_password: str

class UserUpdate(UserBase):
    name: str | None = None
    organization: str | None = None
    email: str | None = None
    role: str | None = None
    disabled: bool
    hashed_password: str | None = None