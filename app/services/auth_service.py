

import jwt
import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, UTC, datetime
from bcrypt import hashpw, gensalt, checkpw
from fastapi import Depends, HTTPException, status
from app.core.config import get_settings, Settings



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Function to hash a password using bcrypt
def hash_password(password: str) -> str:
    pwd = hashpw(password.encode(), gensalt())
    return pwd.decode()

# Function to verify a password against its hashed version
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode(), hashed_password.encode())

# Function to create an access token
def create_access_token(data: dict, settings: Settings, expires_delta: timedelta | None = None) -> str:
    # Create a JWT access token
    to_encode = data.copy()

    # Set the expiration time for the token
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add the expiration time to the token payload
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt #return the encoded JWT token

# Function to verify a token and return the user ID if valid
def verify_token(token: str, settings: Settings) -> str | None:
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
            )
        return payload.get("sub")
    except jwt.InvalidTokenError:
        return None