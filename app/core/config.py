import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

# Configuration settings for the application
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    RESET_SECRET_KEY: str = os.getenv("RESET_SECRET_KEY")
    RESET_ALGORITHM: str = os.getenv("RESET_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AES_MASTER_KEY: str = os.getenv("AES_MASTER_KEY")

#Email configuration settings for the application
class EmailSettings:
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@vaultsecure.com")

# Function to get settings with caching to avoid reloading
@lru_cache()
def get_settings():
    return Settings()


# Function to get email settings with caching to avoid reloading
@lru_cache()
def get_email_settings():
    return EmailSettings()