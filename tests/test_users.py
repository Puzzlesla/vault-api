import pytest

#Test successful user registration
def test_register_success(client):
    response = client.post("/users/register", json={
        "first_name": "Test",
        "last_name": "One",
        "email": "testuser1@example.com",
        "username": "testuser1",
        "password": "testpassword1"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser1"
    assert "id" in data

    assert "password" not in data

#Test registration with an existing username
def test_register_duplicate_username(client):
    user_data = {
        "first_name": "Unique",
        "last_name": "User",
        "email": "uniqueuser@example.com",
        "username": "uniqueuser_test",
        "password": "uniquepassword123"
    }
    # First registration should succeed
    first_response = client.post("/users/register", json=user_data)
    assert first_response.status_code == 201

    # Second registration with the same username should fail
    second_response = client.post("/users/register", json=user_data)
    assert second_response.status_code == 409  # Conflict

    assert second_response.json()["detail"] == "Username 'uniqueuser_test' already exists"

#Test registration with missing password field
def test_register_missing_fields(client):
    response = client.post("/users/register", json={
        "first_name": "Missing",
        "last_name": "Pass",
        "email": "missing@example.com",
        "username": "testuser_missing"
        # Missing password
    })
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data

#Test registration with a password that is too short
def test_register_password_too_short(client):
    response = client.post("/users/register", json={
        "first_name": "Short",
        "last_name": "Pass",
        "email": "short@example.com",
        "username": "testuser_short",
        "password": "123"  # Too short
    })
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data

#Test registration with a username that is too short
def test_get_me_authenticated(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200  # OK
    data = response.json()

    assert "id" in data
    assert "username" in data

#Test getting the current user without authentication
def test_get_me_unauthenticated(client):
    response = client.get("/users/me")
    assert response.status_code == 401  # Unauthorized
    data = response.json()
    assert data["detail"] == "Not authenticated"

#Test updating the current user's own account
def test_update_user_own_account(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    my_id = response.json()["id"]

    response_updated = client.put(
        f"/users/{my_id}", 
        headers=auth_headers, 
        json={
            "username": "updateduser"
        }
    )
    assert response_updated.status_code == 200  # OK
    data = response_updated.json()
    assert data["username"] == "updateduser"

#Test updating another user's account should be rejected
def test_update_user_other_account_rejected(client, auth_headers):
    client.post("/users/register", json={
        "first_name": "Other",
        "last_name": "Person",
        "email": "other_user@example.com",
        "username": "other_user",
        "password": "otherpassword123"
    })

    other_login = client.post("/auth/login", json={
        "username": "other_user",
        "password": "otherpassword123"
    })
    other_token = other_login.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    other_id = client.get("/users/me", headers=other_headers).json()["id"]

    # Try to update other user's account with first user's token
    response = client.put(
        f"/users/{other_id}",
        headers=auth_headers,
        json={"username": "hackeruser"}
    )
    assert response.status_code == 401  # Unauthorized

#Test deleting the current user's own account
def test_delete_user_own_account(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    my_id = response.json()["id"]

    response_deleted = client.delete(f"/users/{my_id}", headers=auth_headers)
    assert response_deleted.status_code == 204  # No Content

    verify_response = client.get(f"/users/{my_id}")
    assert verify_response.status_code == 404  # Not Found

