import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(override=False)

# Configuration settings for the application
class Settings:
    def __init__(self):
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")
        self.SECRET_KEY: str = os.getenv("SECRET_KEY")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.RESET_SECRET_KEY: str = os.getenv("RESET_SECRET_KEY")
        self.RESET_ALGORITHM: str = os.getenv("RESET_ALGORITHM")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        self.AES_MASTER_KEY: str = os.getenv("AES_MASTER_KEY")

#Email configuration settings for the application
class EmailSettings:
    def __init__(self):
        self.SMTP_SERVER: str = os.getenv("SMTP_SERVER")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
        self.SMTP_USER: str = os.getenv("SMTP_USER")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
        self.MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@vaultsecure.com")

# Function to get settings with caching to avoid reloading
@lru_cache()
def get_settings():
    return Settings()


# Function to get email settings with caching to avoid reloading
@lru_cache()
def get_email_settings():
    return EmailSettings()