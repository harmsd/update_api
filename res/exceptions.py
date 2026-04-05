from fastapi import HTTPException, status

def invalid_username_or_password():
    return {
        HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="invalid username or password",
        )
    }

def user_is_disabled():
    return {
        HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user is disabled"
        )
    }

def invalid_token_error():
    return {
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token error"
        )
    }

def token_not_found():
    return {
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token not found"
        )
    }

def user_not_found(): 
    return {
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    }