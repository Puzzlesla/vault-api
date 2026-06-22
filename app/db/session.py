import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .db.base import Base
from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

max_retries = 5
for attempt in range(max_retries):
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
        break
    except OperationalError:
        print(f"Database connection failed. Retrying {attempt + 1}/{max_retries}...")
        time.sleep(5)
else:
    print("Failed to connect to the database after multiple attempts. Please check your database configuration.")
