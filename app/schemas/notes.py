import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=50000)

class NoteResponse(BaseModel):
    id: uuid.UUID
    encrypted_title: str
    encrypted_body: str
    created_at: datetime

class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=50000)

