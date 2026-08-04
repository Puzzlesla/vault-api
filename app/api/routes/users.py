# User routes for the application  
import os
import uuid
import jwt
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings, Settings
from app.services.auth_service import hash_password, verify_password
from app.services.user_service import create_user, get_user_by_username, get_user_by_id, get_user_by_email
from app.db.session import get_db
from app.db.models import User

from app.schemas.user import UserRegister, UserResponse, UserUpdate, EmailUpdate, PasswordResetRequest, PasswordUpdate, PasswordResetConfirm
from app.api.dependencies import get_current_user
from app.utils.email import send_password_reset_email
from app.utils.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)


router = APIRouter(prefix="/users", tags=["users"])

# Environment variables for password reset functionality
FRONTEND_URL = os.getenv("FRONTEND_URL")
RESET_SECRET_KEY = os.getenv("RESET_SECRET_KEY")
RESET_ALGORITHM = os.getenv("RESET_ALGORITHM")

#Register a new user
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    
    # Check if the user already exists
    existing_user = get_user_by_username(user.username, db)
    if existing_user:
        raise UserAlreadyExistsException(f"Username '{user.username}' already exists")

    try:
        new_user = create_user(db, user)
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsException(f"Username '{user.username}' already exists")
    return new_user

#Get current authenticated user info
@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user info."""
    user = verify_user_exists(current_user_id, db)
    return user

#Forgot password request endpoint   
@router.post("/forgot-password")
def forgot_password(payload: PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    #Request a password reset token by providing a valid email
    user = get_user_by_email(payload.email, db)

    if not user:
        return {"message": "Password reset instructions sent to email if it exists in our system"}

    # Generate a short-lived token (expires in 15 minutes)
    expire = datetime.utcnow() + timedelta(minutes=15)
    reset_token = jwt.encode(
        {"sub": str(user.id), "exp": expire}, 
        key=RESET_SECRET_KEY, 
        algorithm=RESET_ALGORITHM
    )
    
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    print(f"Password reset link for {user.email}: {reset_url}")  # For testing purposes

    # Add the email sending task to the background tasks

    background_tasks.add_task(send_password_reset_email, user.email, reset_url)

    # TODO: In production, send this via email. 
    # For testing/dev purposes, returning it lets you test it easily via curl/Postman. Delete this after testing.
    return {
        "message": "Password reset token generated successfully.",
        "reset_token": reset_token  
    }

#Submit a new password along with the reset token to update the user's password.
@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Submit a new password along with the reset token to update the user's password."""
    try:
        payload_data = jwt.decode(payload.token, RESET_SECRET_KEY, algorithms=[RESET_ALGORITHM])
        user_id = payload_data.get("sub")
        if not user_id:
            raise InvalidTokenException("Invalid reset token payload")
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException("Reset token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenException("Invalid reset token")

    #Fetch the user
    user = verify_user_exists(user_id, db)

    #Check that the new password is different from the current password
    if verify_password(payload.new_password, user.password_hash):
        raise InvalidCredentialsException("New password must be different from the current password")

    #Hash the new password and update the model
    user.password_hash = hash_password(payload.new_password)
    
    db.commit()
    db.refresh(user)

    return {"message": "Password reset successfully. You can now log in with your new password."}



@router.get("/{user_id}", response_model=UserResponse)
def get_user_info(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = verify_user_exists(user_id, db)
    return user

#Update username
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """Update user info. Can only update your own account."""
    if user_id != current_user_id:
        raise InvalidCredentialsException("You can only update your own account")

    user = verify_user_exists(user_id, db)
    
    if payload.username:
        existing_user = get_user_by_username(payload.username, db)
        if existing_user and str(existing_user.id) != user_id:
            raise UserAlreadyExistsException(f"Username '{payload.username}' already exists")
        user.username = payload.username
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsException(f"Username '{payload.username}' already exists")

    db.refresh(user)
    return user


#Update email
@router.put("/{user_id}/email", response_model=UserResponse)
def update_email(
    user_id: str,
    payload: EmailUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """Update user email. Can only update your own account."""
    if user_id != current_user_id:
        raise InvalidCredentialsException("You can only update your own account")

    user = verify_user_exists(user_id, db)
    
    if payload.email:
        existing_user = get_user_by_email(payload.email, db)
        if existing_user and str(existing_user.id) != user_id:
            raise UserAlreadyExistsException(f"Email '{payload.email}' already exists")
        user.email = payload.email
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsException(f"Email '{payload.email}' already exists")

    db.refresh(user)
    return user


#Update password
@router.put("/{user_id}/password", status_code=status.HTTP_200_OK)
def update_password(
    user_id: str,
    payload: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """Update user password. Can only update your own password."""
    if user_id != current_user_id:
        raise InvalidCredentialsException("You can only update your own password")

    user = verify_user_exists(user_id, db)

    # Verify that the current password is correct
    if not verify_password(payload.current_password, user.password_hash):
        raise InvalidCredentialsException("Incorrect current password")

    #Check that the new password is different from the current password
    if verify_password(payload.new_password, user.password_hash):
        raise InvalidCredentialsException("New password must be different from the current password")

    # Hash the new password and update the model
    user.password_hash = hash_password(payload.new_password)
    
    db.commit()
    db.refresh(user)

    return {"message": "Password updated successfully"}


#Delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    """Delete user account. Can only delete your own account."""
    if user_id != current_user_id:
        raise InvalidCredentialsException("Not authorized to delete this account")

    user = verify_user_exists(user_id, db)

    try:
        db.delete(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Could not delete user due to related data. Please contact support."
        )

#Helper function to verify user existence
def verify_user_exists(user_id: str, db: Session) -> User:
    """Helper: Verify user exists or raise 404."""
    user = get_user_by_id(user_id, db)
    if not user:
        raise UserNotFoundException("User not found")
    return user