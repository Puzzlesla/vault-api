from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    sub: str | None = None