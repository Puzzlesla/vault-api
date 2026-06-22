import pytest
from app.core.config import Settings



@pytest.fixture
def test_settings():
    from cryptography.fernet import Fernet
    settings = Settings()
    settings.SECRET_KEY = "test-secret-key-that-is-long-enough-for-hs256"
    settings.ALGORITHM = "HS256"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    settings.ENCRYPTION_KEY = Fernet.generate_key().decode()  # Generate a random encryption key for testing
    return settings