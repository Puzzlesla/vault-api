# Database session for the application  

import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.db.base import Base
from app.core.config import get_settings
from sqlalchemy.exc import OperationalError

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Create database tables if they don't exist
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

max_retries = 5
for attempt in range(max_retries):
    try:
        print("Database tables created successfully.")
        break
    except OperationalError:
        print(f"Database connection failed. Retrying {attempt + 1}/{max_retries}...")
        time.sleep(5)
else:
    print("Failed to connect to the database after multiple attempts. Please check your database configuration.")
