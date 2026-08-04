import os
import pytest
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-hs256"
os.environ["ALGORITHM"] = "HS256"
os.environ["RESET_SECRET_KEY"] = "test-reset-secret-key-that-is-long-enough-for-hs256"
os.environ["RESET_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["AES_MASTER_KEY"] = Fernet.generate_key().decode()

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.core.config import Settings, get_settings

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


# Pytest fixtures for testing environment setup
@pytest.fixture(scope="session")
def test_settings():
    settings = Settings()
    settings.SECRET_KEY = "test-secret-key-that-is-long-enough-for-hs256"
    settings.ALGORITHM = "HS256"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    settings.AES_MASTER_KEY = Fernet.generate_key().decode()
    return settings

# Pytest fixture for email settings
@pytest.fixture(scope="session")
def test_email_settings():
    from app.core.config import EmailSettings
    email_settings = EmailSettings()
    email_settings.SMTP_SERVER = "smtp.testserver.com"
    email_settings.SMTP_PORT = 587
    email_settings.SMTP_USER = "testuser"
    email_settings.SMTP_PASSWORD = "testpassword"
    email_settings.MAIL_FROM = "test@example.com"
    return email_settings

# Pytest fixture for database engine
@pytest.fixture(scope="session")
def engine(test_settings):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()
        
    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db, test_settings):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_settings] = lambda: test_settings

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def register_and_login(client, username: str, password: str) -> dict:
    # Register the user
    reg_resp = client.post("/users/register", json={
        "first_name": "Test",
        "last_name": "User",
        "email": f"{username}@example.com",
        "username": username, 
        "password": password
        })
    
    # Login to get the token
    response = client.post("/auth/login", json={"username": username, "password": password})

    #DEBUG SPY
    if response.status_code != 200:
        print(f"\nDEBUG: Login failed with status {response.status_code}")
        print(f"DEBUG: Response body: {response.json()}")
        print(f"DEBUG: Registration body: {reg_resp.json()}")

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_headers(client, request):
    # Use the test function name for unique username per test
    unique_username = f"user_{request.node.name}"
    return register_and_login(client, unique_username, "testpassword123")

@pytest.fixture(scope="function")
def second_user_auth_headers(client, request):
    unique_username = f"sec_user_{request.node.name}"
    return register_and_login(client, unique_username, "secondpassword123")