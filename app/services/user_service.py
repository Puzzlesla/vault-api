import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import User
from app.schemas.user import UserRegister
from app.services.auth_service import hash_password


def create_user(db: Session, user: UserRegister) -> User:
    #Hash the password given
    hashed_password = hash_password(user.password)

    #Create a new User object with the provided details and hashed password
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )

    #Add the new user to the database and commit the transaction
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(new_user)
    return new_user

#Get a user by their username from the database
def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).filter(User.username == username).first()

#Get a user by their ID from the database
def get_user_by_id(user_id: str, db: Session) -> User | None:
    try:
        uuid_obj = uuid.UUID(user_id)
    except ValueError:
        return None
    return db.query(User).filter(User.id == uuid_obj).first() #return User

#Get a user by their email from the database
def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first() #return User
