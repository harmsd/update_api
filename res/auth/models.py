from pydantic import BaseModel

class Token(BaseModel):
    username: str | None = None
    access_token: str
    token_type: str

class TokenData(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    role: str | None = None