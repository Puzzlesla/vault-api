from fastapi import APIRouter, Depends, status
from datetime import datetime, UTC

from app.services.auth_service import verify_password, create_access_token
from app.services.user_service import get_user_by_username
from app.db.session import get_db
from app.core.config import get_settings, Settings

from app.schemas.user import UserLogin
from app.schemas.token import TokenResponse
from app.api.dependencies import get_current_user
from app.util.exceptions import InvalidCredentialsException
from app.schemas.user import UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(username: UserLogin, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    #Find user in database and verify password
    user = get_user_by_username(username.username, db)
    if not user or not verify_password(username.password, user.hashed_password):
        raise InvalidCredentialsException("Invalid username or password")

    #Verify user credentials and return JWT token
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(
        access_token=token, 
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(user_id: str = Depends(get_current_user), settings: Settings = Depends(get_settings)):
    
    new_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    #Handle forgot password logic (e.g., send reset email)
    if email:
        #Check if email exists in database and send reset instructions
        pass
    return {"message": "Password reset instructions sent to email if it exists in our system"}

@router.get("/protected")
def protected_route(user_id: str = Depends(get_current_user)):
    return {"message": "This is a protected route", "user_id": user_id}

@router.post("/logout")
def logout():
    #Handle logout logic (e.g., invalidate token, clear cookies)

    return {"message": "User logged out successfully"}


