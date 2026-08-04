
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Create note model
class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=50000)

# Response model for returning note data
class NoteResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    created_at: datetime

# Model for updating note data
class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=50000)

