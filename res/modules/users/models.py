# models.py

from sqlmodel import SQLModel, Field
from typing import Optional

class UserBase(SQLModel):
    organization: str
    role: str
    email: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    username: str = Field(unique=True, index=True)
    password: bytes
    disabled: bool = False

class UserPublic(UserBase):
    id: int

class UserCreate(SQLModel):
    name: str
    username: str
    password_string: str
    organization: str
    role: str
    email: str

class UserUpdate(SQLModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    disabled: Optional[bool] = None
    password: Optional[bytes] = None