import sys
from cryptography.fernet import Fernet
from app.core.config import get_settings

def verify_secret_key() -> None:
    settings = get_settings()
    secret_key = getattr(settings, "SECRET_KEY", None)
    if not secret_key:
        raise ValueError("SECRET_KEY is not set in environment variables.")
    if len(secret_key) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long for security reasons." f" Current length: {len(secret_key)}")

def verify_algorithm() -> None:
    settings = get_settings()
    algorithm = getattr(settings, "ALGORITHM", None)
    if not algorithm:
        raise ValueError("ALGORITHM is not set in environment variables.")
    allowed_algorithms = ["HS256", "HS384", "HS512"]
    if algorithm not in allowed_algorithms:
        raise ValueError(f"ALGORITHM must be one of {allowed_algorithms}. Current value: {algorithm}")

def verify_access_token_expiry() -> None:
    settings = get_settings()
    expiry = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", None)
    if expiry is None:
        raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES is not set in environment variables.")
    if not isinstance(expiry, (int, float)) or expiry <= 0:
        raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be a positive number.")

def verify_database_url() -> None:
    settings = get_settings()
    db_url = getattr(settings, "DATABASE_URL", None)
    if not db_url:
        raise ValueError("DATABASE_URL is not set in environment variables.")
        #Change to sqlite for testing purposes
    if not db_url.startswith("postgresql://"):
        raise ValueError("DATABASE_URL must start with 'postgresql://'. Current value: {db_url}")

def verify_reset_secret_key() -> None:
    settings = get_settings()
    reset_secret_key = getattr(settings, "RESET_SECRET_KEY", None)
    if not reset_secret_key:
        raise ValueError("RESET_SECRET_KEY is not set in environment variables.")
    if len(reset_secret_key) < 32:
        raise ValueError("RESET_SECRET_KEY must be at least 32 characters long for security reasons." f" Current length: {len(reset_secret_key)}")

def verify_aes_key() -> None:
    settings = get_settings()
    raw_key = getattr(settings, "AES_MASTER_KEY", None)
    if not raw_key:
        raise ValueError("AES_MASTER_KEY is not set in environment variables.")
    try:
        Fernet(raw_key.encode())
    except Exception as e:
        raise ValueError(f"Invalid AES_MASTER_KEY: {e}")


def verify_env(verbose: bool = True) -> None:
    checks = [
        verify_secret_key,
        verify_algorithm,
        verify_access_token_expiry,
        verify_database_url,
        verify_aes_key
    ]
    errors = []
    for check in checks:
        try:
            check()
            if verbose:
                print(f"[ENV CHECK] {check.__name__} passed.")
        except ValueError as e:
            errors.append(str(e))
            if verbose:
                print(f"[ENV CHECK] {check.__name__} failed: {e}")
    if errors:
        print("\n[ENV CHECK] Environment variable verification failed with the following errors:")
        for error in errors:
            print(f" - {error}")
        raise sys.exit(1)
    if verbose:
        print("\n[ENV CHECK] All environment variable checks passed successfully.")

if __name__ == "__main__":
    verify_env()
