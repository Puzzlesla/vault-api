import uuid
from fastAPI import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.dependencies import get_current_user

from app.services.note_service import create_note, get_notes_by_user, get_note_by_id, update_note, delete_note
from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate
from app.utils.crypto import decrypt_data



router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    
    user_uuid = uuid.UUID(user_id)
    new_note = create_note(db, user_uuid, note.title, note.body)
    return NoteResponse(
        id=new_note.id,
        encrypted_title=new_note.encrypted_title,
        encrypted_body=new_note.encrypted_body,
        created_at=new_note.created_at
    )

@router.get("/", response_model=list[NoteResponse])
def get_notes(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):

    user_uuid = uuid.UUID(user_id)
    notes = get_notes_by_user(db, user_uuid)

    response_notes = []
    for note in notes:
        try:
            decrypted_title = decrypt_data(note.encrypted_title)
            decrypted_body = decrypt_data(note.encrypted_body)
        except ValueError:
            print(f"Error decrypting note {note.id}")
            continue
        response_notes.append(
            NoteResponse(
                id=note.id,
                encrypted_title=note.encrypted_title,
                encrypted_body=note.encrypted_body,
                created_at=note.created_at
            )
        )
    return response_notes


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        note_uuid = uuid.UUID(note_id)

    """If note exists but note_id is not a valid UUID, we want to return 404 to avoid leaking information about note existence. 
    Hence catching ValueError and returning 404."""
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    user_uuid = uuid.UUID(user_id)
    note = get_note_by_id(db, note_uuid, user_uuid)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    delete_note(db, note)

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    payload: NoteUpdate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        note_uuid = uuid.UUID(note_id)
        
    # If note_id is not a valid UUID, we want to return 404 to avoid leaking information about note existence.
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    user_uuid = uuid.UUID(user_id)
    note = get_note_by_id(db, note_uuid, user_uuid)
    
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    if payload.title is None and payload.body is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one of title or body must be provided for update")
    
    updated_note = update_note(db, note, title=payload.title, body=payload.body)
    
    final_title = payload.title if payload.title is not None else decrypt_data(updated_note.encrypted_title)
    final_body = payload.body if payload.body is not None else decrypt_data(updated_note.encrypted_body)

    return NoteResponse(
        id=updated_note.id,
        encrypted_title=final_title,
        encrypted_body=final_body,
        created_at=updated_note.created_at
    )