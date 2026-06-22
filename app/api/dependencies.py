from app.services.auth_service import verify_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import get_settings



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), settings = Depends(get_settings)) -> str:
    user_id = verify_token(token, settings)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return user_id