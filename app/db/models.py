import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, TIMESTAMP, func, Uuid, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# User model
class User(Base):
    __tablename__ = "users"

    # Swapped to generic Uuid. SQLAlchemy 2.0 maps this to Python's uuid.UUID automatically.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")

# Note model
class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False
    )
    encrypted_title: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    user = relationship("User", back_populates="notes")