from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_all_chat_boxes(db: Session, user_id: int):
    return db.query(models.ChatBox).filter(models.ChatBox.user_id == user_id).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_chat_box(db: Session, chat_box: schemas.ChatBoxCreate, user_id: int):
    db_chat_box = models.ChatBox(name=chat_box.name, user_id=user_id)
    db.add(db_chat_box)
    db.commit()
    db.refresh(db_chat_box)
    return db_chat_box

def create_chat_message(db: Session, chat_message: schemas.ChatMessageCreate, chat_box_id: int):
    db_chat_message = models.ChatHistory(**chat_message.dict(), chat_box_id=chat_box_id)
    db.add(db_chat_message)
    db.commit()
    db.refresh(db_chat_message)
    return db_chat_message

def get_chat_history(db: Session, chat_box_id: int):
    return db.query(models.ChatHistory).filter(models.ChatHistory.chat_box_id == chat_box_id).order_by(models.ChatHistory.timestamp).all()

def check_chatbox_ownership(db: Session, user_id: int, chat_box_id: int) -> bool:
    chat_box = db.query(models.ChatBox).filter(models.ChatBox.id == chat_box_id, models.ChatBox.user_id == user_id).first()
    return chat_box is not None