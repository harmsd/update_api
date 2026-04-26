from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "auth" / "certs" / "private.pem"
    public_key_path: Path = BASE_DIR / "auth" / "certs" / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()
    secure_cookies: bool = False  # set SECURE_COOKIES=true in production (requires HTTPS)

settings = Settings()