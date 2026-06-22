import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.config import get_settings, Settings
from app.services.auth_service import hash_password
from app.services.user_service import create_user, get_user_by_username, get_user_by_id
from app.db.session import get_db
from app.db.models import User

from app.schemas.user import UserRegister, UserResponse, UserUpdate, PasswordResetRequest
from app.api.dependencies import get_current_user
from app.utils.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """Register a new user."""
    existing_user = get_user_by_username(user.username, db)
    if existing_user:
        raise UserAlreadyExistsException(f"Username '{user.username}' already exists")

    try:
        new_user = create_user(db, user)
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsException(f"Username '{user.username}' already exists")
    return new_user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user info."""
    user = verify_user_exists(current_user_id, db)
    return user

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(reset_request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Handle reset password logic."""
    # Implementation for reset password
    pass


@router.get("/{user_id}", response_model=UserResponse)
def get_user_info(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = verify_user_exists(user_id, db)
    return user


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


def verify_user_exists(user_id: str, db: Session) -> User:
    """Helper: Verify user exists or raise 404."""
    user = get_user_by_id(user_id, db)
    if not user:
        raise UserNotFoundException("User not found")
    return user