
from pydantic import BaseModel, Field, ConfigDict, EmailStr
import uuid
from datetime import datetime

# User schemas for the application  
class UserRegister(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="First name between 1-50 characters")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name between 1-50 characters")
    username: str = Field(..., min_length=3, max_length=50, description="Username between 3-50 characters")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    

class UserLogin(BaseModel):
    username_or_email: str = Field(..., alias="username")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schemas for password reset when forgotten
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50, description="Username between 3-50 characters")

# Schemas for updating user email and password
class EmailUpdate(BaseModel):
    email: EmailStr | None = Field(None, description="Valid email address")

# Schemas for updating authenticated user's password
class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
