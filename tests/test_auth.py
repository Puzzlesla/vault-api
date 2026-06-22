# Test for auth service
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from io import BytesIO
import pytest


client = TestClient(app)

def test_register_user():
    response = client.post("/users/register", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_login_user():
    # First register a user
    client.post("/users/register", json={
        "username": "testuser2",
        "password": "testpassword2"
    })
    
    # Then login with the same credentials
    response = client.post("/auth/login", json={
        "username": "testuser2",
        "password": "testpassword2"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_route():
    # First register and login to get a token
    client.post("/users/register", json={
        "username": "testuser3",
        "password": "testpassword3"
    })
    login_response = client.post("/auth/login", json={
        "username": "testuser3",
        "password": "testpassword3"
    })
    token = login_response.json()["access_token"]
    
    # Access protected route with token
    response = client.get("/auth/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "This is a protected route"
    assert "user_id" in data

def test_invalid_login():
    response = client.post("/auth/login", json={
        "username": "nonexistentuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"

def test_invalid_token():
    response = client.get("/auth/protected", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid authentication credentials"

def test_refresh_token():
    # First register and login to get a token
    client.post("/users/register", json={
        "username": "testuser4",
        "password": "testpassword4"
    })
    login_response = client.post("/auth/login", json={
        "username": "testuser4",
        "password": "testpassword4"
    })
    token = login_response.json()["access_token"]
    
    # Refresh the token
    refresh_response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"