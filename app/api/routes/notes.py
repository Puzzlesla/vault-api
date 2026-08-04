
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.dependencies import get_current_user

from app.services import note_service
from app.db.models import User
from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate
from app.utils.crypto import decrypt_data



router = APIRouter(prefix="/notes", tags=["notes"])

#Create a new note for the authenticated user
@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    # If current_user is a User object, use its id; if it's a string (UUID), convert it to UUID
    user_uuid = current_user.id if isinstance(current_user, User) else uuid.UUID(current_user)
    
    # Create a new note
    new_note = note_service.create_note(db, user_uuid, note.title, note.body)
    
    # Return the new note response
    return NoteResponse(
        id=new_note.id,
        title=note.title,
        body=note.body,
        created_at=new_note.created_at
    )

#Get all notes for the authenticated user
@router.get("/", response_model=list[NoteResponse])
def get_notes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    user_uuid = current_user.id if isinstance(current_user, User) else uuid.UUID(current_user)
    
    # Get all notes for the authenticated user
    notes = note_service.get_notes_by_user(db, user_uuid)
    
    # Decrypt the notes before returning them
    response_notes = []
    for note in notes:
        try:
            decrypted_title = decrypt_data(note.encrypted_title)
            decrypted_body = decrypt_data(note.encrypted_body)
        except ValueError:
            continue
        response_notes.append(
            NoteResponse(
                id=note.id,
                title=decrypted_title,
                body=decrypted_body,
                created_at=note.created_at
            )
        )
    return response_notes

#Delete a note by its ID for the authenticated user
@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """If note exists but note_id is not a valid UUID, we want to return 404 to avoid leaking information about note existence. 
    Hence catching ValueError and returning 404."""

    try:
        note_uuid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    user_uuid = uuid.UUID(user_id)
    note = note_service.get_note_by_id(db, note_uuid, user_uuid)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    note_service.delete_note(db, note)

#Update a note by its ID for the authenticated user
@router.put("/{note_id}", response_model=NoteResponse)
def update_note( note_id: str, payload: NoteUpdate, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        note_uuid = uuid.UUID(note_id)
        
    # If note_id is not a valid UUID, we want to return 404 to avoid leaking information about note existence.
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    user_uuid = uuid.UUID(user_id)
    note = note_service.get_note_by_id(db, note_uuid, user_uuid)
    
    # If the note does not exist, return a 404 error
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # If neither title nor body is provided, return a 400 error
    if payload.title is None and payload.body is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one of title or body must be provided for update")
    
    # Update the note with the provided title and/or body
    updated_note = note_service.update_note(db, note, title=payload.title, body=payload.body)
    
    final_title = payload.title if payload.title is not None else decrypt_data(updated_note.encrypted_title)
    final_body = payload.body if payload.body is not None else decrypt_data(updated_note.encrypted_body)

    # Return the updated note
    return NoteResponse(
        id=updated_note.id,
        title=final_title,
        body=final_body,
        created_at=updated_note.created_at
    )