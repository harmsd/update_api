from sqlmodel import Field, Session, SQLModel, create_engine, select

class UserBase(SQLModel):
    organization: str
    role: str
    email: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=None)
    username: str = Field(unique=True, index=True)
    password: bytes
    disabled: bool = False

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
    disabled: bool | None = None
    hashed_password: str | None = None