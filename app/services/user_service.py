from uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exec import IntegrityError
from app.db.models import User
from app.schemas.user import UserCreate
from app.services.auth_service import hash_password

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    new_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(new_user)
    return new_user

def get_user_by_username(username: str, db: Session) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(user_id: str, db: Session) -> User | None:
    try:
        uuid_obj = uuid.UUID(user_id)
    except ValueError:
        return None
    return db.query(User).filter(User.id == uuid_obj).first()

#Come back to this
def enable_mfa(user_id: str, db: Session) -> User | None:
    user = get_user_by_id(user_id, db)
    if user is None:
        return None
    user.mfa_enabled = True
    db.commit()
    db.refresh(user)
    return user