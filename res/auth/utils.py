from datetime import datetime, timedelta

import jwt
import bcrypt

from config import settings

def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_timedelta: timedelta | None = None,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )

    encoded = jwt.encode(
        payload=payload,                   
        key=private_key, 
        algorithm=algorithm
    )
    return encoded

def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token, 
        public_key,
        algorithms=[algorithm]
    )
    return decoded

def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def validate_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,        
    )









# from datetime import datetime, timedelta, timezone
# from typing import Annotated

# import jwt
# from fastapi import Depends, HTTPException, Request, status
# from fastapi.security import OAuth2PasswordBearer
# from jwt.exceptions import InvalidTokenError
# from pwdlib import PasswordHash

# from auth.models import TokenData
# from database import get_user, SessionDep
# from modules.users.models import User


# SECRET_KEY = "e832c20c1c56530b2026262f57c7014b34389d4cf7a763cb7a92036357dfdc09"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

# password_hash = PasswordHash.recommended()
# DUMMY_HASH = password_hash.hash("dummypassword")

# def verify_password(plain_password, hashed_password):
#     return password_hash.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return password_hash.hash(password)

# async def authenticate_user(session, username: str, password: str):
#     user = await get_user(session, username)
#     if not user:
#         verify_password(password, DUMMY_HASH)
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def verify_access_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             return None
#         return username
#     except InvalidTokenError:
#         return None

# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Autheticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user(SessionDep, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user

# async def get_current_active_user(
#         current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

# async def get_current_user_from_cookie(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет токена")

#     username = verify_access_token(token)
#     if not username:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный или просроченный токен")

#     return {"username": username}