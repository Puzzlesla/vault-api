from pydantic import BaseModel, Field, ConfigDict, EmailStr
import uuid
from datetime import datetime

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username between 3-50 characters")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    


class UserLogin(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    mfa_enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PasswordResetRequest(BaseModel):
    email: EmailStr

class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50, description="Username between 3-50 characters")
