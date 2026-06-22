# Test for auth service
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from io import BytesIO

from app.services.auth_service import hash_password, verify_password, create_access_token, verify_token
import pytest


client = TestClient(app)

def test_hash_and_verify_password():
    hashed = hash_password("mysecretpassword")
    assert hashed != "mysecretpassword"  # Ensure password is hashed
    assert verify_password("mysecretpassword", hashed)  # Ensure correct password verifies

def test_wrong_password_verification():
    hashed = hash_password("mysecretpassword")
    assert not verify_password("wrongpassword", hashed)  # Ensure wrong password does not verify

def test_create_and_verify_token(test_settings):
    token = create_access_token(
            data={"sub": "testuser_id"},
            settings=test_settings,
            expires_delta=timedelta(minutes=30)
    )
    user_id = verify_token(token, test_settings)
    assert user_id == "testuser_id"

def test_expired_token_returns_none(test_settings):
    expired_token = create_access_token(
        data={"sub": "testuser_id"},
        settings=test_settings,
        expires_delta=timedelta(minutes=-1)  # Expire immediately
    )
    user_id = verify_token(expired_token, test_settings)
    assert user_id is None

