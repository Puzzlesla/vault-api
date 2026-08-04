import pytest
from app.db.models import Note
from app.utils.crypto import decrypt_data


def test_create_note(client, auth_headers):
    # Create a new note
    note_data = {
        "title": "Encrypted Title",
        "body": "Encrypted Body"
    }
    #Fetch the response from the API and assert that the title and body are returned in plaintext
    response = client.post("/notes/", headers=auth_headers, json=note_data)
    assert response.status_code == 201 
    data = response.json()

    assert "id" in data
    assert "created_at" in data

    # Assert directly against the plaintext returned by the API
    assert data["title"] == note_data["title"]
    assert data["body"] == note_data["body"]


def test_get_notes_returns_plaintext(client, auth_headers):
    note_data = {
        "title": "Plaintext check",
        "body": "Should come back decrypted"
    }
    client.post("/notes/", headers=auth_headers, json=note_data)

    response = client.get("/notes/", headers=auth_headers)
    assert response.status_code == 200  # OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least one note should be present

    note = next(n for n in data if n["title"] == "Plaintext check")
    assert note["title"] == "Plaintext check"
    assert note["body"] == "Should come back decrypted"
    
    # Confirm it doesn't look like ciphertext
    assert not note["title"].startswith("gAAAAA")
    assert not note["body"].startswith("gAAAAA")

def test_db_stores_ciphertext(client, auth_headers, db):
    note_data = {
        "title": "Ciphertext check",
        "body": "This should be stored encrypted"
    }
    response = client.post("/notes/", headers=auth_headers, json=note_data)
    assert response.status_code == 201  # Created
    note_id = response.json()["id"]

    from uuid import UUID
    db_note = db.query(Note).filter(Note.id == UUID(note_id)).first()

    assert db_note is not None

    assert db_note.encrypted_title != "Ciphertext check"  # Should be encrypted
    assert db_note.encrypted_body != "This should be stored encrypted"  # Should be encrypted

    assert db_note.encrypted_title.startswith("gAAAAA")  # Fernet ciphertext prefix
    assert db_note.encrypted_body.startswith("gAAAAA")  # Fernet ciphertext prefix

def test_update_note(client, auth_headers):
    note_data = {
        "title": "Original Title",
        "body": "Original Body"
    }
    response = client.post("/notes/", headers=auth_headers, json=note_data)
    assert response.status_code == 201  # Created
    note_id = response.json()["id"]

    # Update the note
    update_data = {
        "title": "Updated Title",
        "body": "Updated Body"
    }
    #Update just the title
    update_title_response = client.put(f"/notes/{note_id}", headers=auth_headers, json={"title": update_data["title"]})
    assert update_title_response.status_code == 200  # OK

    updated_note = update_title_response.json()
    assert updated_note["title"] == "Updated Title"
    assert updated_note["body"] == "Original Body"  # Body should remain unchanged

    #Update just the body
    update_body_response = client.put(f"/notes/{note_id}", headers=auth_headers, json={"body": update_data["body"]})
    assert update_body_response.status_code == 200  # OK

    updated_note = update_body_response.json()
    assert updated_note["title"] == "Updated Title"  # Title should remain unchanged
    assert updated_note["body"] == "Updated Body"

def test_delete_note(client, auth_headers):
    note_data = {
        "title": "To be deleted",
        "body": "This note will be deleted"
    }
    response = client.post("/notes/", headers=auth_headers, json=note_data)
    assert response.status_code == 201  # Created
    note_id = response.json()["id"]

    # Delete the note
    delete_response = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert delete_response.status_code == 204  # No Content

    # Verify the note is deleted
    get_response = client.get("/notes/", headers=auth_headers)
    assert get_response.status_code == 200  # OK
    notes = get_response.json()
    assert all(note["id"] != note_id for note in notes)

def test_cannot_delete_other_users_note(client, auth_headers):
    # Create a note with the first user
    note_data = {
        "title": "User1's Note",
        "body": "This note belongs to User1"
    }
    response = client.post("/notes/", headers=auth_headers, json=note_data)
    assert response.status_code == 201  # Created
    note_id = response.json()["id"]

    # Register and login as a second user
    client.post("/users/register", json={
        "first_name": "Delete",
        "last_name": "Tester",
        "email": "delete_user2@example.com",
        "username": "delete_user2",
        "password": "password123"
        })
    login_response = client.post("/auth/login", json={
        "username": "delete_user2",
        "password": "password123"})
    token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {token}"}

    # Attempt to delete the first user's note with the second user's token
    delete_response = client.delete(f"/notes/{note_id}", headers=user2_headers)
    assert delete_response.status_code == 404  # Not Found, since the note doesn't belong to user2

    note_response = client.get("/notes/", headers=auth_headers).json()
    assert any(note["id"] == note_id for note in note_response)  # Note

def test_cannot_update_other_users_note(client, auth_headers):
    # Create a note with the first user
    note_data = {
        "title": "User1's Note",
        "body": "This note belongs to User1"
    }
    response = client.post("/notes/", headers=auth_headers, json=note_data)
    assert response.status_code == 201  # Created
    note_id = response.json()["id"]

    # Register and login as a second user
    client.post("/users/register", json={
        "first_name": "Update",
        "last_name": "Tester",
        "email": "update_user2@example.com",
        "username": "update_user2",
        "password": "password123"
        })
    login_response = client.post("/auth/login", json={
        "username": "update_user2", 
        "password": "password123"})
    token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {token}"}

    # Attempt to update the first user's note with the second user's token
    update_data = {
        "title": "Hacked Title",
        "body": "Hacked Body"
    }
    update_response = client.put(f"/notes/{note_id}", headers=user2_headers, json=update_data)
    assert update_response.status_code == 404  # Not Found, since the note doesn't belong to user2

    #Confirm the note remains unchanged for user1
    note_response = client.get("/notes/", headers=auth_headers).json()
    original_note = next(note for note in note_response if note["id"] == note_id)
    assert original_note["title"] == "User1's Note"