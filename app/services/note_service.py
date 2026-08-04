
import uuid
from sqlalchemy.orm import Session
from app.db.models import Note
from app.utils.crypto import encrypt_data


def create_note(db: Session, user_id: uuid.UUID, title: str, body: str) -> Note:
    #Create a new note for user
    new_note = Note(
        user_id=user_id,
        encrypted_title=encrypt_data(title),
        encrypted_body=encrypt_data(body)
    )

    #Add to the database and commit the transaction
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

#Get all notes for a specific user
def get_notes_by_user(db: Session, user_id: uuid.UUID) -> list[Note]:
    return db.query(Note).filter(Note.user_id == user_id).all()

#Get a specific note by its ID for a specific user
def get_note_by_id(db: Session, note_id: uuid.UUID, user_id: uuid.UUID) -> Note | None:
    """Fetch a note by its ID, ensuring it belongs to the specified user.
    Used for delete - enforces ownership at the query level to prevent unauthorized access."""
    return (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == user_id)
        .first()
    )

#Update a note's title and/or body for a specific user
def update_note(db: Session, note: Note, title: str | None = None, body: str | None = None) -> Note:
    #Check if title or body is provided, and update accordingly
    if title is not None:
        note.encrypted_title = encrypt_data(title)
    if body is not None:
        note.encrypt_body = encrypt_data(body)
    db.commit()
    db.refresh(note)
    return note

#Delete a note for a specific user
def delete_note(db: Session, note: Note) -> None:
    db.delete(note)
    db.commit()
    return note