
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from datetime import datetime, UTC, timedelta
from app.services.auth_service import create_access_token, verify_token
from app.services.user_service import get_user_by_id

from app.services.auth_service import verify_password, create_access_token
from app.services.user_service import get_user_by_username
from app.db.session import get_db
from app.core.config import get_settings, Settings


from app.schemas.user import UserLogin
from app.db.models import User
from app.schemas.token import TokenResponse
from app.api.dependencies import get_current_user
from app.utils.exceptions import InvalidCredentialsException
from app.schemas.user import UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])

#Login endpoint for user authentication
@router.post("/login", response_model=TokenResponse)
def login(username: UserLogin, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):

    #Check if the input string matches a username OR an email
    user = db.query(User).filter(
        (User.username == username.username_or_email) | 
        (User.email == username.username_or_email)
    ).first()

    # Verify user exists and password is correct
    if not user or not verify_password(username.password, user.password_hash):
        raise InvalidCredentialsException("Invalid username/ or password")

    #Verify user credentials and return JWT token
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        settings=settings
    )
    #Return the token response 
    return TokenResponse(
        access_token=token, 
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

#Refresh token endpoint to issue a new JWT token
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(user_id: str = Depends(get_current_user), settings: Settings = Depends(get_settings)):
    #Generate a new JWT token for the authenticated user
    new_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        settings=settings
    )
    #Return the new token response
    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

#Protected route to verify JWT token validity
@router.get("/protected")
def protected_route(user_id: str = Depends(get_current_user)):
    return {"message": "This is a protected route", "user_id": user_id}

#Logout endpoint for user logout
@router.post("/logout")
def logout(user_id: str = Depends(get_current_user)):
    # Stateless JWT — nothing to invalidate server-side.
    # Real logout handled client-side by discarding the token from sessionStorage.
    return {"message": "User logged out successfully"}

