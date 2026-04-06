# res/exceptions.py
from fastapi import HTTPException, status

invalid_username_or_password = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid username or password",
)

user_is_disabled = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="user is disabled",
)

invalid_token_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token error",
)

token_not_found = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="token not found",
)

user_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)