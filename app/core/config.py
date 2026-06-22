import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AES_MASTER_KEY: str = os.getenv("AES_MASTER_KEY")

@lru_cache()
def get_settings():
    return Settings()